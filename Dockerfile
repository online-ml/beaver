FROM python:3.9

WORKDIR /app

RUN pip3 install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . /app

ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "--port", "3000"]
CMD ["examples.wsgi:dam.http_server"]