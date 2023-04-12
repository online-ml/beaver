FROM python:3.10

WORKDIR /code

RUN pip3 install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
RUN pip install river

COPY . /code
