FROM python:3.14-rc-alpine3.21

LABEL maintainer="github.com/heschmat"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt ./requirements.dev.txt /tmp/

COPY ./backend /app

WORKDIR /app

EXPOSE 8000

# By default DEV is false.
ARG DEV=false

# Set PATH to include the virtual environment
# /py/bin is being prepended to the PATH variable
# now we can simply use `pip` rather than `/py/bin/pip`
ENV PATH="/py/bin:$PATH"

RUN python -m venv /py && \
    pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base \
        postgresql-dev \
        musl-dev && \
    pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    # Remove the packages that were only required for psycopg2 installation.
    apk del .tmp-build-deps && \
    # DO NOT use the root user.
    adduser --disabled-password --no-create-home django-user

USER django-user
