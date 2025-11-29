FROM python:3.11-slim

# Install texlive for LaTeX compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv for dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Create assets directory
RUN mkdir -p assets

EXPOSE 8000

# Run with waitress for production
CMD ["uv", "run", "waitress-serve", "--listen=0.0.0.0:8000", "app:app"]
