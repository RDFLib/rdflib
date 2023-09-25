FROM docker.io/library/python:3.11.5-slim@sha256:edaf703dce209d774af3ff768fc92b1e3b60261e7602126276f9ceb0e3a96874

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
