# Use the official Python image from the Docker Hub
FROM python:3.8.3-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py", "bot"]