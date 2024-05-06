import pyarrow.parquet as pq
import pandas as pd
import numpy as np
from sentence_transformers import util

def get_data(_path):
    pand_t = pq.read_table(_path).to_pandas()
    nump_t = pand_t.to_numpy()

    authors_dict = dict()
    for row in nump_t:
        if row[1] in authors_dict:
            authors_dict[row[1]]['articles'] += [{'id': row[2], 'title': row[3], 'abstract': row[4],
                                                  'emb': row[5], 'score': 0}]
        else:
            authors_dict[row[1]] = {'name': row[0], 'articles': [{'id': row[2], 'title': row[3], 'abstract': row[4],
                                                                  'emb': row[5], 'score': 0}], 'total_score': 0}
    return authors_dict

def search(_query, _top_number, data_dict, model):
    result = {'№': [], 'Имя': [], 'Оценка релевантности': [], 'link': [], 'Релевантная статья 1': [], 'a_a title 1': [],
              'Релевантная статья 2': [], 'a_a title 2': [],
              'Релевантная статья 3': [], 'a_a title 3': [], }

    query_emb = model.encode(_query, normalize_embeddings=True)

    for author in data_dict:
        art_num = len(data_dict[author]['articles'])
        try:
            if art_num >= 3:
                for article_ind in range(art_num):
                    data_dict[author]['articles'][article_ind]['score'] = float(
                        util.dot_score(data_dict[author]['articles'][article_ind]['emb'], query_emb))
                data_dict[author]['articles'] = sorted(data_dict[author]['articles'],
                                                           key=lambda k: k['score'], reverse=True)

                data_dict[author]['total_score'] = (np.exp(np.array([data_dict[author]['articles'][i]['score']
                                                                         for i in range(3)]))).mean()
        except Exception as e:
            print(repr(e))
            print(author, len(data_dict[author]['articles']))
    data_dict = dict(sorted(data_dict.items(), key=lambda item: item[1]['total_score'], reverse=True))
    i = 0
    number = 1
    try:
        for author in data_dict:
            result['№'] += [number]
            result['Имя'] += [data_dict[author]['name']]
            result['Оценка релевантности'] += [data_dict[author]['total_score']]
            result['link'] += [author]
            result['Релевантная статья 1'].append(data_dict[author]['articles'][0]['id'])
            result['Релевантная статья 2'].append(data_dict[author]['articles'][1]['id'])
            result['Релевантная статья 3'].append(data_dict[author]['articles'][2]['id'])
            result['a_a title 1'].append(data_dict[author]['articles'][0]['title'])
            result['a_a title 2'].append(data_dict[author]['articles'][1]['title'])
            result['a_a title 3'].append(data_dict[author]['articles'][2]['title'])
            if i == _top_number:
                break
            i += 1
            number += 1
    except:
        print('add')
    _result = pd.DataFrame(result)
    _result['Имя'] = '<a href="' + _result['link'] + '">' + _result['Имя'] + '</a>'
    try:
        _result['Релевантная статья 1'] = '<a href="' + _result['Релевантная статья 1'] + '">' + _result[
            'a_a title 1'] + '</a>'
        _result['Релевантная статья 2'] = '<a href="' + _result['Релевантная статья 2'] + '">' + _result[
            'a_a title 2'] + '</a>'
        _result['Релевантная статья 3'] = '<a href="' + _result['Релевантная статья 3'] + '">' + _result[
            'a_a title 3'] + '</a>'
    except:
        print('re')
    try:
        _result.drop('link', axis=1, inplace=True)
        _result.drop('a_a title 1', axis=1, inplace=True)
        _result.drop('a_a title 2', axis=1, inplace=True)
        _result.drop('a_a title 3', axis=1, inplace=True)
    except:
        print('drop')
    return _result.to_html(escape=False, index=False)
