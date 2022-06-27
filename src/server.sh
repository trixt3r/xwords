#!/bin/bash
source /home/vhamon/.virtualenvs/new3/bin/activate
cd words
python server.py&
sleep 10
cd ..
cd flask_server
/home/vhamon/.virtualenvs/new3/bin/gunicorn --pythonpath ../ flask_server.flask_server:app
