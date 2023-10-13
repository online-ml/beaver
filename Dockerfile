FROM python:3.10

WORKDIR /code

RUN pip3 install poetry

COPY pyproject.toml poetry.lock ./
COPY sdk/ ./sdk
RUN poetry config virtualenvs.create false
RUN poetry install --with ui --no-interaction --no-ansi
RUN pip install river
