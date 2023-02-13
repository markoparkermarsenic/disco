FROM python:3.6-slim

ENV DEBUG=True
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir -p /opt/app/
WORKDIR /opt/app

COPY app /opt/app
COPY requirements.txt /opt/app/requirements.txt



RUN cd /opt/app

RUN python -m pip install -r requirements.txt


CMD ["./run.sh"]
