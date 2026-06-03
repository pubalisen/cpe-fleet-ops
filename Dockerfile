FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent source, skills, and eval sets
COPY app/ ./app/

# Ensure .adk directories exist and are writable
RUN mkdir -p /app/app/.adk/eval_sets /app/app/.adk/eval_history /app/.adk/artifacts && chmod -R 777 /app/.adk /app/app/.adk

# Cloud Run injects PORT env var (default 8080)
EXPOSE 8080

CMD ["sh", "-c", "adk web --port ${PORT:-8080} --host 0.0.0.0"]
