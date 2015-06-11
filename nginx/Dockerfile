FROM nginx


RUN apt-get update
RUN apt-get install -y python
RUN apt-get install -y python-pip
RUN pip install click

RUN mkdir /scripts
COPY nginx.template.conf /scripts/nginx.template.conf
COPY conf_creator.py /scripts/conf_creator.py
COPY docker-entrypoint.sh /scripts/docker-entrypoint.sh
RUN mkdir /logs

EXPOSE 80

CMD bash /scripts/docker-entrypoint.sh
