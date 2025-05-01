FROM python:3.11-slim

WORKDIR /app

# Install the greenlet package explicitly to fix SQLAlchemy issues
RUN pip install greenlet

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Set environment variables
ENV PORT=8000

# Command to run the application when the container starts
CMD python -m uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-8000} --timeout-keep-alive=300 