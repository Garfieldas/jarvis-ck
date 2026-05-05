FROM python:latest
ENV PYTHONUNBUFFERED=1

# Set the working directory to /phoenix
WORKDIR /webPerformers

# copy the requirements file used for dependencies
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt --upgrade
# Install web-p
RUN apt-get update && \
    apt-get install -y webp
RUN apt-get install -y imagemagick
RUN apt install -y gettext

# Copy the rest of the working directory contents into the container at /app
COPY . .

# These line for /deployment/web/webCommands.sh
# COPY /deployment/web/webCommands.sh webCommands.sh
# RUN chmod +x deployment/web/webCommands_init.sh
RUN chmod +x web/runServer.sh