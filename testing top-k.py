import lucene
from tqdm import tqdm
import pickle

from java.io import File
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search.similarities import LMJelinekMercerSimilarity, BM25Similarity, LMDirichletSimilarity


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


def test_top_k(_k_list, _path, _similarity, _analyzer):
    with open('test_articles.pkl', 'rb') as _file:
        _test_articles = pickle.load(_file)
    _directory = open_directory(_path)
    _searcher = make_searcher(_directory, _similarity)

    _too_long = 0
    _result_top_k = dict.fromkeys(_k_list, 0)
    _max_k = max(_k_list)
    for _author, _abstract in tqdm(_test_articles.items()):
        if len(_abstract.split()) <= 1000:
            _top_authors = score_authors(_searcher, _abstract, _analyzer, _max_k)
            _names = get_field('name', _top_authors, _searcher)
            for _k in _k_list:
                if _author in _names[:_k]:
                    _result_top_k[_k] += 1
        else:
            _too_long += 1
    del _searcher

    _number_of_tests = len(_test_articles.keys()) - _too_long
    print('too long queries: ', _too_long)
    for _k, _result in _result_top_k.items():
        print(f'\ttop {_k}:\t{_result/_number_of_tests}')



if __name__ == '__main__':
    lucene.initVM()
    test_top_k([1, 5, 10], 'index', LMJelinekMercerSimilarity(0.7), EnglishAnalyzer())


