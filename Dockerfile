FROM python:3.11
ENV PYTHONUNBUFFERED=1 \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1

WORKDIR /code

COPY pyproject.toml poetry.lock /code/
RUN pip install poetry && poetry install --no-root --no-directory

COPY bot/ /code/src/
RUN poetry install --no-dev

ENTRYPOINT ["poetry","run","python", "/code/src/__init__.py"]