FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc curl
RUN pip install --upgrade pip
RUN curl -sSL https://install.python-poetry.org | python3

ENV PATH="/root/.local/bin:$PATH"
ENV POETRY_VIRTUALENVS_CREATE=false

COPY pyproject.toml poetry.lock README.md ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY mysite19 .

EXPOSE 8000

# Для gunicorn
#CMD ["gunicorn", "mysite19.wsgi:application", "--bind", "0.0.0.0:8000"]
