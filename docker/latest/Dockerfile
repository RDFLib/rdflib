FROM docker.io/library/python:3.11.3-slim@sha256:5a67c38a7c28ad09d08f4e153280023a2df77189b55af7804d7ceb96fee6a68f

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
