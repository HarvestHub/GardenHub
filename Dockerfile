FROM python:3.5-alpine

MAINTAINER HarvestHub

RUN apk add --update \
    python-dev \
    build-base \
    linux-headers \
    pcre-dev \
    py-pip \
    nodejs \
    # Pillow depenencies
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
    tk-dev \
    tcl-dev \
  && rm -rf /var/cache/apk/*

ADD . /app
WORKDIR /app

RUN npm install && \
    npm install -g less && \
    pip install -r /app/requirements.txt

RUN python manage.py collectstatic --noinput && \
    python manage.py compress --force

CMD ["gunicorn", "wsgi", "-b 0.0.0.0:5000"]
