FROM python:3.11-slim-bullseye

RUN apt update && \
    apt install -y --no-install-recommends iputils-ping && \
    apt clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/ && \
    useradd --create-home --no-log-init --shell /bin/bash electricitybot && \
    chmod o+rwx /opt
COPY . /opt/

RUN chown -R electricitybot:electricitybot /opt/*
USER electricitybot

WORKDIR /opt

RUN export PATH=${PATH}:~/.local/bin/ && \
    python -m pip install poetry && \
    poetry install && \
    touch .env && \
    chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
