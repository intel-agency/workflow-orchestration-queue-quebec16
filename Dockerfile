# OS-APOW Dockerfile
# Python 3.12 slim base with UV package manager

FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Install UV package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy source code BEFORE installing (required for uv pip install -e .)
COPY src/ ./src/
COPY pyproject.toml ./

# Install dependencies using UV
RUN uv pip install --system -e .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port for FastAPI
EXPOSE 8000

# Default command runs the notifier service
CMD ["uvicorn", "os_apow.services.notifier:app", "--host", "0.0.0.0", "--port", "8000"]
