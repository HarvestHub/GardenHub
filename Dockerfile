FROM python:3.7-alpine

MAINTAINER HarvestHub

# Makes manage.py commands able to show output
ENV PYTHONUNBUFFERED 1

ADD requirements.txt /requirements.txt

RUN set -ex \
    # Install build dependencies
    && apk add --no-cache --virtual .build-deps \
        # General build dependencies
        python-dev \
        build-base \
        linux-headers \
        pcre-dev \
        # Pillow build depenencies
        jpeg-dev \
        zlib-dev \
        freetype-dev \
        lcms2-dev \
        openjpeg-dev \
        tiff-dev \
        tk-dev \
        tcl-dev \
        # Postgres build dependencies
        postgresql-dev \
    # Upgrade pip
    && pip install -U pip \
    # Install requirements.txt
    && pip install --no-cache-dir -r /requirements.txt \
    # Install gunicorn
    && pip install --no-cache-dir gunicorn \
    # Scans project and collects runtime dependencies
    && runDeps="$( \
        scanelf --needed --nobanner --recursive \
            $(python -c 'import site; print(site.getsitepackages()[0])') \
            | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
            | sort -u \
            | xargs -r apk info --installed \
            | sort -u \
    )" \
    # Install Node and Less for compiling .less in development
    && apk add --no-cache npm \
    && npm install -g less \
    # Add the runtime dependencies we need to keep
    && apk add --virtual .python-rundeps $runDeps \
    # Delete the build dependencies we no longer need
    && apk del .build-deps

WORKDIR /app
ADD . /app

RUN set -ex \
    # Collect static files for production
    && python manage.py collectstatic --noinput \
    # Compile static files for production
    && python manage.py compress --force

CMD ["gunicorn", "wsgi", "-b :5000"]
