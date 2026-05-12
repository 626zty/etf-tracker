FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    chromium \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chromium

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
