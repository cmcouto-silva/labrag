FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Copy requirements and README first for better caching
COPY pyproject.toml uv.lock README.md ./

# Install dependencies  
RUN uv sync --all-extras --frozen

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p data/vector_store data/raw/papers

# Expose ports
EXPOSE 8000 8501

# Activate the virtual environment
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Default command (will be overridden in docker-compose)
CMD ["uvicorn", "labrag.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
