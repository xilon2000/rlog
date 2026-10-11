FROM python:3.14-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/app

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

COPY --chown=appuser:appuser ./app ./app
COPY --chown=appuser:appuser ./tests ./tests
COPY --chown=appuser:appuser ./pytest.ini ./

EXPOSE 8000

ARG APP_MODULE
ENV APP_MODULE=${APP_MODULE}

CMD ["sh", "-c", "exec uvicorn ${APP_MODULE} --host 0.0.0.0 --port 8000"]