FROM docker.io/library/python:3.12.4-slim@sha256:f11725aba18c19664a408902103365eaf8013823ffc56270f921d1dc78a198cb

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
