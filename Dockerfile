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

RUN npm install -g less

ADD . /app
WORKDIR /app

RUN pip install -r /app/requirements.txt

RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

EXPOSE 80

CMD ["gunicorn", "wsgi", "-b 0.0.0.0:5000"]
