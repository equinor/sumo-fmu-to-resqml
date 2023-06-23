# syntax=docker/dockerfile:1

FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

USER 1001
CMD [ "python", "-m" , "flask", "--app", "app/app", "run", "--host=127.0.0.1" ]
EXPOSE 5000