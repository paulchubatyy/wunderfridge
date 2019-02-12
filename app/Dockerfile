FROM python:3.7
RUN pip install --no-cache-dir pipenv
ADD . /app
WORKDIR /app
RUN pipenv install --system --deploy --ignore-pipfile
