FROM python:3.12.2-slim

WORKDIR /srv/

COPY pyproject.toml .
COPY poetry.lock .

RUN apt update && apt upgrade -y && pip install 'poetry<2.0'

RUN poetry config virtualenvs.create false
RUN poetry install

RUN apt-get remove -y gcc cmake make libc-dev-bin libc6-dev
RUN rm -rf /var/lib/apt/lists/* && apt-get autoremove -y && apt-get clean
RUN pip uninstall pipenv poetry -y

COPY . .
