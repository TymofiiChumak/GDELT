# GDELT

## Set Google Cloud Credentials 
for using BigQuery API for GDELT database you need to specify 
account Google Cloud credentials ([Use this page](https://console.cloud.google.com/apis/credentials/serviceaccountkey)).
Firstly login to you google account. Then as "Service account" choose "New service account".
Fill "Service account name" by any name you want. As role select "BigQuery" -> "Big Query User".
Choose JSON key type. Finally download key file by "Create" button. 
Rename file as ```google_cloud_credentials.json```, 
and place it to ```GDELT/resources/google_cloud_credentials.json```. 

![](https://github.com/TymofiiChumak/GDELT/raw/develop/readme_images/bigquery1.png)

![](https://github.com/TymofiiChumak/GDELT/raw/develop/readme_images/bigquery2.png)

## Install dependencies

To use tis app you must have python 3. To install dependencies:
```shell
pip3 install django gunicorn plotly-express google-cloud-bigquery
```

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

## Mapbox access token
If you want to use your own mapbox account, you need to place 
you access token to `GDELT/resources/mapbox_tocken`. 
To create a new token go to this [page](https://account.mapbox.com/access-tokens/create). 
