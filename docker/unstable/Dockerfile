FROM docker.io/library/python:3.11.1-slim@sha256:073caf67fbbfad42fbadc5a7282edec4fb88cb53a177318f46991acf9a0c30c1

# This file is generated from docker:unstable in Taskfile.yml
COPY var/requirements.txt /var/tmp/build/

RUN \
    pip install -r /var/tmp/build/requirements.txt

COPY dist/*.whl /var/tmp/build/

RUN \
    pip install --no-deps /var/tmp/build/*.whl && \
    rdfpipe --version

ENTRYPOINT [ ]
