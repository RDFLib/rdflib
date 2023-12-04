FROM docker.io/library/python:3.12.0-slim@sha256:19a6235339a74eca01227b03629f63b6f5020abc21142436eced6ec3a9839a76

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
