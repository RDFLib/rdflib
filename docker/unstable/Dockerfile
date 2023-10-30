FROM docker.io/library/python:3.12.0-slim@sha256:babc0d450bf9ed2b369814bc2f466e53a6ea43f1201f6df4e7988751f755c52c

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
