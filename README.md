# Expert-Finding
ссылка на датасет: https://github.com/allenai/cord19

Также в репозитории присутствует собственный датасет, сформированный командой.
# Инструкции по установке pylucene (Windows)
1) скачиваем docker desktop
2) открываем, ищем в поиске pylucene, скачиваем самую популярную image coady/pylucene
3) заходим в терминал, вбиваем `docker run -it -p 8888:8888 coady/pylucene:latest` (для простой работы с `.ipynb` в дальнейшем), в приложении docker должен появиться запущенный контейнер.
4) в VsCode устанавливаем расширение docker и в соответствующей вкладке открываем запущенный контейнер с pylucene в новом окне.
5) через терминал внутри контейнера устанавливаем jupyter `pip install jupyter`
6) запускаем jupyter используя команду `jupyter notebook --ip 0.0.0.0 --port 8888 --no-browser --allow-root`
7) открываем любой `.ipynb` файл, во вкладке Select kernel вставляем ссылку на сервер.
