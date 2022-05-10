@echo off
echo celery...

echo activate
call "C:\Users\ducker\PycharmProjects\virtualenvs\e-shop\Scripts\activate"

echo dir

call "C:\Users\ducker\PycharmProjects\virtualenvs\e-shop\"

celery -A tasks worker -P solo -E --loglevel=info

celery -A task beat --loglevel=info
pause