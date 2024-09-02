FROM docker.io/library/python:3.12.5-slim@sha256:59c7332a4a24373861c4a5f0eec2c92b87e3efeb8ddef011744ef9a751b1d11c

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
