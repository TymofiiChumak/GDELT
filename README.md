# GDELT

## Set Google Cloud Credentials 
for using BigQuery API for GDELT database you need to specify 
account Google Cloud credentials. Firstly [create project](https://console.cloud.google.com/projectcreate).
Just enter a project name (e.g. "GDELT"), and set location as "No organization".

![](https://github.com/TymofiiChumak/GDELT/raw/develop/readme_images/bigquery3.png)
![](https://github.com/TymofiiChumak/GDELT/raw/develop/readme_images/bigquery4.png)

Then [use this page](https://console.cloud.google.com/apis/credentials/serviceaccountkey)
to create a new credentials for project.
Choose as "Service account" choose "New service account".
Fill "Service account name" by any name you want. As role select "BigQuery" -> "Big Query User".
Choose JSON key type. Finally download key file by "Create" button. 
Rename file as ```google_cloud_credentials.json```, 
and place it to ```GDELT/resources/google_cloud_credentials.json```. 

![](https://github.com/TymofiiChumak/GDELT/raw/develop/readme_images/bigquery1.png)

![](https://github.com/TymofiiChumak/GDELT/raw/develop/readme_images/bigquery2.png)

## Install dependencies

To use tis app you must have python 3. To install dependencies:
```shell
pip3 install django plotly-express google-cloud-bigquery folium mapboxgl chart_studio ipython
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
