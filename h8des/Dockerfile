ARG BASE_IMAGE_TAG=python3.12-bookworm-slim
ARG PYTHON_IMAGE_TAG=3.12-slim-bookworm

# Build stage with uv for dependency resolution and installation
FROM ghcr.io/astral-sh/uv:${BASE_IMAGE_TAG} AS builder

WORKDIR /app

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1

# Copy project metadata and source code
COPY pyproject.toml .
COPY h8des ./h8des

# Create a virtual environment and install the package
RUN uv venv /app/.venv && \
    uv pip install --no-cache .

# Runtime stage with minimal Python image
FROM python:${PYTHON_IMAGE_TAG}

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Ensure the venv binaries are used
ENV PATH="/app/.venv/bin:$PATH"

# Set the entrypoint to the package's console script
ENTRYPOINT ["vpc-metrics"]
