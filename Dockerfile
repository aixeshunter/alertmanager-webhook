FROM    cbankieratypon/python-2.7-flask
LABEL   maintainer="Aixes Hunter <aixeshunter@gmail.com>"

ADD   alerts.py  /opt
ADD   start.sh   /opt

# ENV http_proxy "http://127.0.0.1:1080"
RUN pip install flask-sqlalchemy
# RUN unset http_proxy

RUN   mkdir -p /var/lib/alerts
RUN   chmod 755 -R /var/lib/alerts
RUN   chmod 755 -R /opt/start.sh

EXPOSE 5000

ENTRYPOINT  [ "/opt/start.sh" ]