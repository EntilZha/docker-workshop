FROM python:2.7

ENV PYTHONUNBUFFERED 1

RUN mkdir /web
ADD requirements.txt /web/requirements.txt
WORKDIR /web
RUN pip install -r requirements.txt

VOLUME /web
ADD . /web

EXPOSE 8000

ENTRYPOINT "/web/docker-entrypoint.sh"
