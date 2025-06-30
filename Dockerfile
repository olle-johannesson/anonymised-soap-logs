FROM python:3.12-slim

# Set up work directory
WORKDIR /app

# Copy source code
COPY *.py /app/

# Install dependencies
RUN pip install --no-cache-dir faker

# Run CLI wrapper
ENTRYPOINT ["python", "run.py"]
