FROM docker.io/library/python:3.11.0rc2-slim@sha256:a7b7703e1479bce7e911341cac76c3cad4d1b7efa794f03fc2df17155152fef0

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
