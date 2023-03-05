FROM docker.io/library/python:3.11.2-slim@sha256:64eb3661444eb66fa45d5aaaba743f165990235dd7da61a1f5042c61e98da37a

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
