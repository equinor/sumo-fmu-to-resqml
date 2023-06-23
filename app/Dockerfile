# syntax=docker/dockerfile:1

FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

USER 1001
CMD [ "flask", "--app", "app", "run", "--host=0.0.0.0"]