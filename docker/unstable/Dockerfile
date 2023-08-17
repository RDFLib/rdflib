FROM docker.io/library/python:3.11.2-slim@sha256:d0e839882b87135b355361efeb9e9030c9d2a808da06434f4c99eb4009c15e64

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
