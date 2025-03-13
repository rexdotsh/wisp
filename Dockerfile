FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE ${PORT}

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:${PORT}", "--workers", "4", "--timeout", "120", "--preload", "--log-level", "info", "--access-logfile", "/dev/stdout", "--error-logfile", "/dev/stderr"]
