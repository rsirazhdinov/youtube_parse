# youtube_parse
Для запуска скрипта необходимо установить Redis:
sudo apt-get install redis-server

Затем установить модули:
pip install aioredis
pip install aiohttp
pip install asyncio

<b>Формулировка Задачи:</b>
Собрать данные для запросов к поиску Youtube (любым способом). мин 100 000 запросов. Можно даже просто перебрать цифры от 1...100 000
Результат нужно сохранить в виде. 'запрос' ---> 'video_id', как и где значение не имеет.
Желательно пояснить какие решения и для чего были приняты.

<b>Пояснения к выбору технологий:</b>
Посылается GET запрос вида https://www.youtube.com/results?search_query=52947&page=1&sp=EgIQAQ%253D%253D&persist_gl=1&gl=US, где search_query варьируется от 1 до 100000. Для большого количество запросов была выбрана библиотека aiohttp c возможностью асинхронных запросов.
Результаты сохранялись в redis как в хранилице с высокой скоростью записи.

<b>Тестирование:</b> 100000 запросов выполнялись ~1900 с
