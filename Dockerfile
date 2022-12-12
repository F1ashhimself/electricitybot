FROM python:3.11-slim-bullseye

COPY . /opt

WORKDIR /opt

RUN apt update && \
    apt install -y --no-install-recommends make iputils-ping && \
    python -m pip install poetry && \
    poetry install && \
    touch .env && \
    chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
