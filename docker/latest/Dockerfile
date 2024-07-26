FROM docker.io/library/python:3.12.4-slim@sha256:52f92c54e879539342692d20a4bea99516d4a2eb3cd16dfbb4e4b964aa8becaa

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
