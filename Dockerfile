# To run: docker run -v /path/to/wsgi.py:/var/www/amanuensis/wsgi.py --name=amanuensis -p 81:80 amanuensis
# To check running container: docker exec -it amanuensis /bin/bash

FROM quay.io/cdis/python-nginx:pybase3-1.4.1

RUN apk update \
    && apk add postgresql-libs postgresql-dev libffi-dev libressl-dev \
    && apk add linux-headers musl-dev gcc libxml2-dev libxslt-dev \
    && apk add curl bash git vim

COPY . /amanuensis
COPY ./deployment/uwsgi/uwsgi.ini /etc/uwsgi/uwsgi.ini
WORKDIR /amanuensis

RUN python -m pip install --upgrade pip \
    && python -m pip install --upgrade setuptools \
    && pip --version \
    && pip install -r requirements.txt 
    # && pip uninstall authlib -y \
    # && pip install authlib==0.14.2

RUN mkdir -p /var/www/amanuensis \
    && mkdir /run/ngnix/ \
    && chown nginx /var/www/amanuensis

EXPOSE 80

RUN COMMIT=`git rev-parse HEAD` && echo "COMMIT=\"${COMMIT}\"" >amanuensis/version_data.py \
    && VERSION=`git describe --always --tags` && echo "VERSION=\"${VERSION}\"" >>amanuensis/version_data.py \
    && python setup.py install

WORKDIR /var/www/amanuensis

CMD /dockerrun.sh
