# Base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Collect static files (optional)
RUN mkdir -p /vol/static
RUN python manage.py collectstatic --noinput || echo "collectstatic failed"

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
