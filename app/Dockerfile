FROM arm32v7/python:3.7-slim
RUN pip install --no-cache-dir pipenv
ADD . /app
WORKDIR /app
RUN pipenv install --deploy --ignore-pipfile
