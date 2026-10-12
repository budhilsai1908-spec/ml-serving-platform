# Start from a slim, official Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /code

# Copy requirements first (for better build caching)
COPY requirements.txt .

# Install dependencies, no cache to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and the trained model
COPY app/ ./app/

# Document the port the app listens on
EXPOSE 8000

# The command that starts the server when the container runs
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
