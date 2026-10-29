FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --upgrade setuptools==82.0.1 wheel==0.46.2

COPY app.py .

RUN useradd --create-home appuser

USER appuser

EXPOSE 5000

CMD ["python", "app.py"]