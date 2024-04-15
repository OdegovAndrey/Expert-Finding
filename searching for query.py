import lucene
import re

from java.io import File
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search.similarities import LMJelinekMercerSimilarity, BM25Similarity, LMDirichletSimilarity


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
        return re.split(r'[ ,.]',_query[_query.find(_token):])[0]

def get_details(_top_authors, _query, _details_number, _searcher, _analyzer):
    _result = []
    _parsed_query = QueryParser("abstract", _analyzer).parse(_query)
    for _author in _top_authors:
        _raw_details =_searcher.explain(_parsed_query, _author.doc).getDetails()
        _details = []
        for _raw_detail in _raw_details:
            _detail = _raw_detail.toString()
            _details.append([float(_detail.split()[0]), _detail.split(':')[1].split()[0]])
        _top_details = sorted(_details, key=lambda _detail: -_detail[0])[:_details_number]
        _result.append('')
        for _detail in _top_details:
            _result[-1] += f"{recover(_detail[1], query):<15s}{_detail[0]:4.1f}|| "
    return _result

def search_for_query(_query, _top_number, _details_number, _path, _similarity, _analyzer):
    _query = cleaner(_query)
    _directory = open_directory(_path)
    _searcher = make_searcher(_directory, _similarity)
    _top_authors = score_authors(_searcher, _query, _analyzer, _top_number)
    _names = get_field('name', _top_authors, _searcher)
    _scores = get_scores(_top_authors)
    _details = get_details(_top_authors, _query, _details_number, _searcher, _analyzer)
    del _searcher
    for _number in range(_top_number):
        print(f"{_number + 1:<5}{_names[_number]:30s}{_scores[_number]:.3f}     |" + _details[_number])


if __name__ == '__main__':
    lucene.initVM()
    with open('query.txt', 'r') as file:
        query = "\n".join(file.readlines())
    search_for_query(query, 10, 5, 'index', LMJelinekMercerSimilarity(0.7), EnglishAnalyzer())

