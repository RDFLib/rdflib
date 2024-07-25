FROM docker.io/library/python:3.12.4-slim@sha256:52f92c54e879539342692d20a4bea99516d4a2eb3cd16dfbb4e4b964aa8becaa

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
