FROM python:3.11-slim

WORKDIR /app

# Install Python deps in a separate layer so source-only changes don't bust the cache.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the server source.
COPY . .

# Create a non-root user and hand it ownership of the working dir.
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8100

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]
