FROM docker.io/library/python:3.11.2-slim@sha256:64eb3661444eb66fa45d5aaaba743f165990235dd7da61a1f5042c61e98da37a

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
