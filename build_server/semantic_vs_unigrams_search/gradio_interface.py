import lucene
import os
import gradio as gr
import pandas as pd
from sentence_transformers import SentenceTransformer
from build_server.semantic_vs_unigrams_search import search_semantic, search_unigrams

from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.search.similarities import LMJelinekMercerSimilarity

data = search_semantic.get_data(os.environ.get("PATH_TO_DATA"))
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2').to('cpu')

def gradio_search_unigrams(_query, _top_number, _details_number):
    print(_query)
    _vm_env = lucene.getVMEnv()
    _vm_env.attachCurrentThread()
    try:
        _result = search_unigrams.search_for_query(_query, _top_number, _details_number, 'index', LMJelinekMercerSimilarity(0.7), EnglishAnalyzer())
    except Exception as e:
        print(repr(e))
        _result = pd.DataFrame({'Некорректный запрос': []}).to_html(escape=False, index=False)
    _result = '<div style="display: block; width: 100%; overflow-x: auto;">' + _result + '</div>'
    return _result

def gradio_search_semantic(_query, _top_number, ):
    print(_query)
    try:
        _result = search_semantic.search(_query, _top_number, data, model)
    except Exception as e:
        print(repr(e))
        _result = pd.DataFrame({'Некорректный запрос': []}).to_html(escape=False, index=False)
    _result = '<div style="display: block; width: 100%; overflow-x: auto;">' + _result + '</div>'
    return _result

if __name__ == '__main__':
    lucene.initVM()

    theme = gr.themes.Soft(
    primary_hue=gr.themes.Color(c100="#54b686", c200="#e5e7eb", c300="#d1d5db", c400="#434242", c50="#f3f2f2", c500="#ffffff", c600="#54b686", c700="#374151", c800="#1f2937", c900="#111827", c950="#0b0f19"),
    ).set(
    link_text_color='*primary_100',
    link_text_color_dark='*primary_100',
    link_text_color_active='*primary_100',
    link_text_color_active_dark='*primary_100',
    link_text_color_hover='*primary_100',
    link_text_color_hover_dark='*primary_100',
    link_text_color_visited='*primary_100',
    link_text_color_visited_dark='*primary_100',
    block_background_fill='*primary_50',
    block_label_text_color_dark='*primary_400',
    block_title_text_color_dark='*primary_400',
    slider_color='*primary_100',
    button_primary_background_fill='*primary_100',
    button_primary_background_fill_hover_dark='*primary_100'
    )

    with gr.Blocks(theme=theme, fill_height='Expert finding') as interface:

        gr.Markdown(
        """
        # Поиск ученого НГУ по запросу(*) пользователя
        Программа предназначена для поиска экспертов по заданной пользователем теме.\n
        Поиск осуществляется только по **сотрудникам НГУ**: по базе данных, состоящей из **аннотаций к статьям сотрудников**.\n
        **В интерфейсе представлено два метода поиска эксперта:**\n
        **Метод 1** использует **языковую модель униграмм** с интерполяцией с фиксированным коэффициентом (**Jelinek-Mercer smoothing**).\n 
        **Метод 2** использует языковую модель, отображающую предложения и абзацы в 384-мерное плотное векторное пространство (**MiniLM-L6-v2**).\n
        Чтобы найти эксперта, в поле **"Запрос"** введите описание интересующей вас темы и нажмите **"Показать"**. 
        После нажатия кнопки **"Показать"** выведется список экспертов по теме. 
        Имя эксперта является гиперссылкой на профиль эксперта на OpenAlex.\n
        Помимо имени эксперта, в таблице в столбце **"Оценка релевантности"** содержится оценка релевантности эксперта заданной теме. 
        Для **Метода 1** и **Метода 2** **оценка релевантности** вычисляется по-разному и описана ниже в поле **"Результаты..."** для каждого метода.\n
        - Вы можете изменить отображаемое количество экспертов, подвинув слайдер **"Количество экспертов"**. 
        Программа покажет число экспертов, не превосходящее числа, установленного на слайдере. По умолчанию программа показывает 10 экспертов.\n
        **(*)** _Запрос должен быть сформулирован на английском языке и содержать не более 1000 слов._\n
        _Примеры запросов:_\n
        > _The target compounds will be obtained, isolated and characterized using modern tools of synthetic and physical organic chemistry using cross-combination reactions, condensation. 
        Using the methods of crystallization from solution, as well as the method of physical steam transport (FPT), crystalline samples of the studied compounds will be obtained, their structure and morphology will be studied using microscopy methods. 
        The crystal structure of the studied compounds will be determined by X-ray diffraction analysis. 
        The sensory properties of the obtained compounds and materials will be studied in a solution of various analytes and in the solid phase when exposed to various stimuli. 
        The most effective positions of nitrogen atoms in fluorenes will be revealed, as well as the most advantageous options for joining linear, conformationally mobile, planar, substituted structures for obtaining promising materials for organic photonics, electronics and sensors._
        \n
        > _Markov chain_
        """)

        input_text = gr.Textbox(label="Запрос", placeholder="Чем подробнее вы опишите тему, тем более релевантных экспертов покажет программа")
        slider_people = gr.Slider(1, 50, value=10, step=1, label="Количество экспертов")
        button = gr.Button("Показать", variant="primary")
        with gr.Tab("Поиск по униграммам"):
            gr.Markdown("""# Результаты поиска по униграммам
                        **Оценка релевантности** складывается из весов ключевых слов.\n
                        В столбцах типа **"Слово N: вес"** указаны слова, наибольшим образом повлиявшие на оценку релевантности эксперта. Для каждого слова указан его вес.\n
                        - Вы можете изменить отображаемое количество столбцов **"Слово N: вес"**, подвинув слайдер **"Количество столбцов "Слово N: вес""** на значение N. 
                        По умолчанию такие столбцы отсутствуют.""")
            slider_tokens = gr.Slider(0, 20, step=1, label='Количество столбцов "Слово N: вес"')
            output_name_1 = gr.HTML(label="Список экспертов", show_label=True)
        with gr.Tab("Семантический поиск"):
            gr.Markdown("""# Результаты семантического поиска
                        **Оценка релевантности** является средневзвешенной оценкой **трех наиболее релевантных запросу статей** автора.
                        Оценивание производится путем применения exp(x) к оценкам релевантности статей и вычисления среднего значения
                        полученных exp(x).\n
                        - В столбцах типа **"Релевантная статья N"** указаны три **наиболее релевантные запросу статьи**, по которым строится оценка релевантности.""")
            output_name_2 = gr.HTML(label="Список экспертов", show_label=True)

        button.click(fn=gradio_search_unigrams, inputs=[input_text, slider_people, slider_tokens], outputs=output_name_1)
        button.click(fn=gradio_search_semantic, inputs=[input_text, slider_people], outputs=output_name_2)

    if os.environ.get("ISDOCKER", None):
        interface.launch(share=False, debug=True, server_name="0.0.0.0", server_port=7860)
    else:
        interface.launch(share=True)
