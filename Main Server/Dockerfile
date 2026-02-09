# Use the official Python 3.8 slim image as the base image
FROM python:3.8-slim

# Set the working directory within the container
WORKDIR /main-server

# Copy the necessary files and directories into the container
COPY server/ .env run.py requirements.txt /main-server/
COPY server/ /main-server/server/
COPY .env run.py requirements.txt  /main-server/

# Upgrade pip and install Python dependencies
RUN pip3 install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for the Flask application
EXPOSE 5000

# Define the command to run the Flask application using Gunicorn
CMD ["gunicorn", "run:app", "-b", "0.0.0.0:5000", "-w", "1"]