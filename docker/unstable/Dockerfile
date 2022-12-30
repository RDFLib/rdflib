FROM docker.io/library/python:3.11.1-slim@sha256:8f3997244336ad0f067ad693f85906263a21a7f571b6577a64134aba889bc95e

COPY docker/unstable/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
