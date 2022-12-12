FROM docker.io/library/python:3.11.1-slim@sha256:555dcc94587b4101de48664b45b19f17e099a3ab236dec629791f366e2f2e83c

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
