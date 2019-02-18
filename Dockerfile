FROM    centos
LABEL   maintainer="aixeshunter@hikvision.com.cn"


# ENV http_proxy "http://127.0.0.1:6555"
# ENV https_proxy "http://127.0.0.1:6555"
RUN rm -rf /etc/yum.repos.d/*.repo
ADD epel.repo /etc/yum.repos.d
ADD CentOS-Base.repo /etc/yum.repos.d
RUN yum clean all && yum makecache &&  yum -y install python2-pip && pip install flask flask-sqlalchemy
# RUN unset http_proxy
# RUN unset https_proxy
ADD   alerts.py  /opt
ADD   start.sh   /opt

RUN   mkdir -p /var/lib/alerts
RUN   chmod 755 -R /var/lib/alerts
RUN   chmod 755 -R /opt/start.sh


EXPOSE 5000

ENTRYPOINT  [ "/opt/start.sh" ]
