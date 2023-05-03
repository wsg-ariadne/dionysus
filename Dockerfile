FROM python:3.8-slim AS dependencies

# Install psycopg2 build dependencies
RUN apt-get update && apt-get install -y libpq-dev build-essential

# Install pip requirements under virtualenv
RUN pip install --upgrade pip wheel
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
COPY requirements.txt .
RUN pip install -r requirements.txt

# Replace opencv-python with the headless version
RUN pip uninstall opencv-python -y && pip install opencv-python-headless


FROM python:3.8-slim AS runtime
COPY --from=dependencies /opt/venv /opt/venv
LABEL maintainer="Jared Dantis <jareddantis@gmail.com>"

# Install psycopg2 runtime and healthcheck dependencies
RUN apt-get update && apt-get install -y libpq-dev curl

# Copy bot files and specify environment variables
COPY . /opt/app
WORKDIR /opt/app
ENV PATH="/opt/venv/bin:${PATH}"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


FROM runtime AS production
ENTRYPOINT ["python3", "-m", "gunicorn"]


FROM runtime AS development
ENV FLASK_APP=main.py
ENV FLASK_DEBUG=1
ENTRYPOINT ["python3", "-m", "flask", "run", "--host", "0.0.0.0", "--port", "5000"]
