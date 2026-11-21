FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home appuser
COPY . .
USER appuser
EXPOSE 8080
CMD ["gunicorn", "tutberry.wsgi:application", "--bind", "0.0.0.0:8080", "--access-logfile", "-"]
