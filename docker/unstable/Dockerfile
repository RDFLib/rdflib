FROM docker.io/library/python:3.10-slim@sha256:c212a18a48efd4de1d6455f197538563d9cc312775761f14c50866c9a7eabd0e

COPY docker/unstable/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
