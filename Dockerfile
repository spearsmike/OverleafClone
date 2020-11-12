FROM python:3.8.6
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install -y sqlite3 libsqlite3-dev
RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt
