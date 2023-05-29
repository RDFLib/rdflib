FROM docker.io/library/python:3.11.3-slim@sha256:eaee5f73efa9ae962d2077756292bc4878c04fcbc13dc168bb00cc365f35647e

COPY docker/latest/requirements.txt /var/tmp/build/

RUN \
    pip install --no-deps -r /var/tmp/build/requirements.txt && \
    rdfpipe --version

ENTRYPOINT [ ]
