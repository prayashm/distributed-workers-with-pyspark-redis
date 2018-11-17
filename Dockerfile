FROM python:3.6-onbuild

COPY debian/debian-jessie-backports.list /etc/apt/sources.list.d/
COPY debian/debian-jessie-backports /etc/apt/preferences.d/
RUN apt-get update

RUN apt-get -t jessie-backports install -y openjdk-8-jdk
RUN pyspark --packages com.databricks:spark_csv_2.10

COPY . .

ENV PORT 8080
CMD python api.py