FROM balenalib/raspberrypi3-ubuntu-python:3.6-trusty-build
RUN apt-get update && apt-get install -y python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir pipenv
ADD Pipfile.lock Pipfile /tmp/
WORKDIR /tmp
RUN pipenv install --system --deploy --ignore-pipfile
ADD . /app
WORKDIR /app
