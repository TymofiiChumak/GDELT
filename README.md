# GDELT

## Run application server 
Run from main directory of project:
```shell
python manage.py runserver
```
To use virtual environment:
```shell
/venv/bin/python manage.py runserver
```
To use docker:
```shell
docker build -t gdelt-web-app Docker/
docker run --rm -v $(pwd):/home/gdelt -p 8000:8000 gdelt-web-app
```
