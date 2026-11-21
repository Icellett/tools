FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./

ARG INSTALL_DEV=false

RUN if [ "$INSTALL_DEV" = "true" ]; then \
        pip install --no-cache-dir -r requirements-dev.txt; \
    else \
        pip install --no-cache-dir -r requirements.txt; \
    fi && useradd --create-home appuser

COPY . .

USER appuser

EXPOSE 8080

CMD ["gunicorn", "tutberry.wsgi:application", "--bind", "0.0.0.0:8080", "--access-logfile", "-"]