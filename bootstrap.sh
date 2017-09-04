#!/bin/sh
if [ ! -e /etc/vagrant/nginx ]
then
    apt-get update -y
    apt-get install -y nginx
    cat /vagrant/nginx.default.conf > /etc/nginx/sites-available/default
    service nginx restart

    apt-get install -y python-pip
    pip install virtualenv
    pip install -r /vagrant/requirements.txt
    python /vagrant/manage.py migrate
    python /vagrant/manage.py collectstatic -v0 --noinput
    pip install gunicorn
    cd /vagrant
    /usr/local/bin/gunicorn --access-logfile - --workers 3 --bind unix:/vagrant/impactoestrategico.sock impactoestrategico.wsgi:application -D

else
    echo "[+] nginx ya está instalado."
fi
