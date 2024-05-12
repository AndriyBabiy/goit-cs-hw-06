# The docker system will use the Python 3.12-slim instance of Python
FROM python:3.10

ENV APP_DIR /app

# We outline the core directory of our application to be the ENV variable set above
WORKDIR ${APP_DIR}

# Copy the other files into the working directory of the container
COPY requirements.txt ./

# Outline the dependencies within the container
RUN pip install -r requirements.txt 

COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Execute the app within the container
ENTRYPOINT [ "python", "main.py" ]