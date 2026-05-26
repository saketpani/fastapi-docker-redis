FROM python:3.12-slim

# Enforce stable, non-buffered Python system output environments
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install baseline curl for health checking and create a secure non-root system user
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -u 10001 -m appuser

# Leverage Docker caching layers for system dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application assets and hand file permissions to the application user
COPY app/ .
RUN chown -R appuser:appuser /app

# Switch runtime privileges entirely away from root context
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]