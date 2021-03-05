FROM python:3.8.5

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /CHATAPI

WORKDIR /CHATAPI

COPY . /CHATAPI/

RUN pip install --upgrade pip && pip install pip-tools && pip install -r requirements.txt
