#!/bin/sh
while inotifywait -r -e modify,create,delete,move .; do
    pgrep uwsgi | xargs kill -9
    if [ -f ./wsgi.py ]; then
        printf "\napplication.debug=True\n\n" >> ./wsgi.py
    fi

    if [ -z $DD_ENABLED ]; then
    (
        uwsgi --ini /etc/uwsgi/uwsgi.ini
    ) &
    else
        pip install ddtrace
        echo "import=ddtrace.bootstrap.sitecustomize" >> /etc/uwsgi/uwsgi.ini
    (
        ddtrace-run uwsgi --enable-threads --ini /etc/uwsgi/uwsgi.ini
    ) &
    fi
done