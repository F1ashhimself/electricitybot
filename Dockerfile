FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/F1ashhimself/electricitybot.git" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="electricitybot" \
      org.opencontainers.image.description="Bot that will send telegram message in case of electricity state was changed"

RUN apt-get update && \
    apt-get install -y --no-install-recommends iputils-ping && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/ && \
    useradd --create-home --no-log-init --shell /bin/bash electricitybot && \
    chmod o+rwx /opt
COPY . /opt/

RUN chown -R electricitybot:electricitybot /opt/*
USER electricitybot

WORKDIR /opt

RUN export PATH="${PATH}":~/.local/bin/ && \
    python -m pip install --no-cache-dir poetry==1.2.2 && \
    poetry install && \
    chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
