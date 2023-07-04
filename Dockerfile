# syntax=docker/dockerfile:1

FROM python:3.11-slim-buster

WORKDIR /fmu-to-resqml

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN chown -R 1001:1001 /fmu-to-resqml
USER 1001
CMD [ "python", "-m" , "flask", "--app", "fmu-to-resqml/app", "run", "--host=0.0.0.0" ]
EXPOSE 5000