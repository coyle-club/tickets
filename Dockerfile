FROM docker.io/python:3.10.4-alpine

COPY tickets /app/tickets

COPY setup.py /app/setup.py

RUN pip install -e /app

ENTRYPOINT ["/usr/local/bin/gunicorn"]
CMD ["--access-logfile", "-", "tickets:app"]


