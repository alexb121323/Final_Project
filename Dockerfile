#Use an offical python runtime as the parent image
FROM python:3.11-slim-bookworm
# Set a working directory in the container call /app
WORKDIR /app
# Copy the current directory contents into the container /app directory
COPY . /app
#Copy the requirements.txt
COPY requirements.txt requirements.txt
#Upgrade pip
RUN pip install --upgrade pip
# Install required python modules from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt



EXPOSE 5019
#Set the default command to run when starting container
CMD ["python", "app.py"]