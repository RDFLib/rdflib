FROM docker.io/library/python:3.11.3-slim@sha256:551c9529e77896518ac5693d7e98ee5e12051d625de450ac2a68da1eae15ec87

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
