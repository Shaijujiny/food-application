# Use an official Python runtime as the base image
FROM python:3.12-slim
 
# Set the working directory inside the container
WORKDIR /app
 
# Copy the requirements file to the working directory
COPY requirements.txt .
 
RUN pip install --upgrade pip
# Install the application dependencies
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy the application code to the working directory
COPY . .


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]