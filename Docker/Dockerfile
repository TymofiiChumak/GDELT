FROM ubuntu:19.04
WORKDIR /home/gdelt
RUN apt-get update; apt-get -y install python3 python3-pip
RUN pip3 install django gunicorn plotly-express google-cloud-bigquery
ENTRYPOINT gunicorn GDELT.wsgi:application --bind 0.0.0.0:8000 --workers 3