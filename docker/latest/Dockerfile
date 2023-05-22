FROM docker.io/library/python:3.11.3-slim@sha256:551c9529e77896518ac5693d7e98ee5e12051d625de450ac2a68da1eae15ec87

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
