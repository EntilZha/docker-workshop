#!/usr/bin/env bash
HOST_IP=`ip route show 0.0.0.0/0 | grep -Eo 'via \S+' | awk '{ print \$2 }'`
python /scripts/conf_creator.py /scripts/nginx.template.conf /etc/nginx/nginx.conf $HOST_IP
nginx
