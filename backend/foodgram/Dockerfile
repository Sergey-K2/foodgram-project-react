FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt /app

RUN apt-get update -y \
    && apt-get upgrade -y pip \
    && pip install --upgrade pip 

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY . /app

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ] 
