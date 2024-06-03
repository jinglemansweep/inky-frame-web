FROM python:3.10-bullseye

ARG user="user"
ARG uid="1001"

ENV PYTHONUNBUFFERED=1
ENV SLEEP_DELAY=3600

RUN useradd -rm -d /home/${user} -s /bin/bash -u ${uid} ${user}

RUN mkdir /opt/workspace && \
    chown -R ${user}:${user} /opt/workspace

RUN pip install --upgrade poetry pip
COPY pyproject.toml poetry.lock /opt/workspace/

WORKDIR /opt/workspace

RUN python -m venv ./venv && \
    . ./venv/bin/activate && \
    poetry install

USER ${user}
COPY . .

ENTRYPOINT ["/opt/workspace/venv/bin/python", "-m", "inkyframeweb"]

HEALTHCHECK CMD curl --fail http://localhost:5665/status/health || exit 1
