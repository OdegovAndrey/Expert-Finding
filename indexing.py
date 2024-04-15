import lucene
import pandas
from tqdm import tqdm
import pickle
import re

from java.io import File
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import FSDirectory


def cleaner(_string):
    if type(_string) is str:
        _regular = re.compile('[^a-zA-Z .,]')
        return re.sub(' +', ' ', _regular.sub(' ', _string))
    return ''
    
def make_writer(_analyzer, _directory):
    return IndexWriter(_directory, IndexWriterConfig(_analyzer))

def open_directory(_path):
    return FSDirectory.open(File(_path).toPath())

def clean_directory(_directory):
    for _file in _directory.listAll():
        _directory.deleteFile(_file)

def index_document(_writer, _name, _text):
    _tft = FieldType()
    _tft.setStored(True)
    _tft.setTokenized(True)
    _tft.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS_AND_OFFSETS)
    _document = Document()
    _document.add(Field("name", _name, _tft))
    _document.add(Field("abstract", _text, _tft))
    _writer.addDocument(_document)


def index_data(_data_authors, _data_abstracts, _path, _minimum_articles, _minimal_length, _analyzer):
    _directory = open_directory(_path)
    clean_directory(_directory)

    _authors = {}
    _incorrect = 0
    for _number, _author in enumerate(_data_authors):
        _abstract = cleaner(_data_abstracts[_number])
        if len(_abstract) >= _minimal_length:
            if _author in _authors:
                _authors[_author] += [_abstract]
            else:
                _authors[_author] = [_abstract]
        else:
            _incorrect += 1

    _test_articles = {}
    _writer = make_writer(_analyzer, _directory)
    for _author in tqdm(_authors.keys()):
        if len(_authors[_author]) >= _minimum_articles:
            _test_articles[_author] = _authors[_author][0]
            index_document(_writer, _author, '\n'.join(_authors[_author][1:]))
    _writer.close()

    with open('test_articles.pkl', 'wb') as _file:
        pickle.dump(_test_articles, _file)

    print('total articles: ', len(_data_abstracts))
    print('incorrect data rows: ', _incorrect)
    print('total authors before filtering: ', len(_authors.keys()))
    print('total authors after filtering: ', len(_test_articles.keys()))


if __name__ == '__main__':
    lucene.initVM()

    with open('data.csv') as f_in:
        data = pandas.read_csv(f_in, sep=';')
    data_authors = list(data['Author name'])
    data_abstracts = list(data['Article abstract'])

    index_data(data_authors, data_abstracts, 'index', 5, 50, EnglishAnalyzer())
