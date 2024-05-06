import re
import pandas as pd
from java.io import File
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher

def cleaner(_string):
    if type(_string) is str:
        _regular = re.compile('[^a-zA-Z .,]')
        return re.sub(' +', ' ', _regular.sub(' ', _string))
    return ''

def make_searcher(_directory, _similarity):
    _searcher = IndexSearcher(DirectoryReader.open(_directory))
    _searcher.setSimilarity(_similarity)
    return _searcher

def open_directory(_path):
    return FSDirectory.open(File(_path).toPath())

def score_authors(_searcher, _query, _analyzer, _top_number):
    _parsed_query = QueryParser("abstract", _analyzer).parse(_query)
    return _searcher.search(_parsed_query, _top_number).scoreDocs

def get_field(_field_name, _top_authors, _searcher):
    return [_searcher.doc(_author.doc).get(_field_name) for _author in _top_authors]

def get_scores(_top_authors):
    return [_author.score for _author in _top_authors]

def recover(_token, _query):
    if _query.find(_token) == -1:
        return _token
    else:
        _query = ' ' + cleaner(_query).lower()
        return re.split(r'[ ,.]',_query[_query.find(' ' + _token) + 1:])[0]

def get_details(_top_authors, _query, _details_number, _searcher, _analyzer):
    _result = []
    _parsed_query = QueryParser("abstract", _analyzer).parse(_query)
    for _author in _top_authors:
        _raw_details = _searcher.explain(_parsed_query, _author.doc).getDetails()
        if len(_raw_details) == 1 and _details_number > 0:
            _raw_detail = _searcher.explain(_parsed_query, _author.doc).toString()
            _detail = [float(_raw_detail.split()[0]), _raw_detail.split('abstract:')[1].split()[0]]
            _result.append([f"{recover(_detail[1], _query)}:{_detail[0]:6.1f}"])
        elif len(_raw_details) > 1:
            _details = []
            for _raw_detail in _raw_details:
                _detail = _raw_detail.toString()
                _details.append([float(_detail.split()[0]), _detail.split('abstract:')[1].split()[0]])
            _top_details = sorted(_details, key=lambda _detail: -_detail[0])[:_details_number]
            _result.append([])
            for _detail in _top_details:
                _result[-1] += [f"{recover(_detail[1], _query)}:{_detail[0]:6.1f}"]
        else:
            _result.append([])
    return _result

def search_for_query(_query, _top_number, _details_number, _path, _similarity, _analyzer):
    _query = cleaner(_query)
    _directory = open_directory(_path)
    _searcher = make_searcher(_directory, _similarity)
    _top_authors = score_authors(_searcher, _query, _analyzer, _top_number)
    _names = get_field('name', _top_authors, _searcher)
    _links = get_field('link', _top_authors, _searcher)
    _scores = get_scores(_top_authors)
    _details = get_details(_top_authors, _query, _details_number, _searcher, _analyzer)
    del _searcher

    _data_frame = {"№": [], "Имя": [], "Оценка релевантности":[], "link": []}
    for _detail_number in range(_details_number):
        _data_frame[f"Слово {_detail_number + 1}: вес"] = [None for _ in range(len(_names))]
    for _name_number in range(len(_names)):
        _data_frame["№"] += [_name_number + 1]
        _data_frame["Имя"] += [f"{_names[_name_number]}"]
        _data_frame["link"] += [f"{_links[_name_number]}"]
        _data_frame["Оценка релевантности"] += [f"{_scores[_name_number]:.1f}"]
        for _detail_number, _detail in enumerate(_details[_name_number]):
                _data_frame[f"Слово {_detail_number + 1}: вес"][_name_number] = '<p align="center">' +  _detail + '</p>'
    _result = pd.DataFrame(_data_frame)
    _result["Имя"] = '<a href="' + _result["link"] + '">' +  _result["Имя"] + '</a>'
    _result.drop('link', axis= 1 , inplace= True)
    _result["Оценка релевантности"] = '<p align="center">' +  _result["Оценка релевантности"] + '</p>'
    return _result.to_html(escape=False, index=False)
