ARG VERSION=3.12
FROM python:$VERSION

#Label for application
ARG COMMIT
ARG APP_VERSION
ARG BUILD_TIME

LABEL \
    ck.app.commit=$COMMIT \
    ck.app.version=$APP_VERSION \
    ck.image.title="CK Socket Server" \
    ck.image.created="$BUILD_TIME"

WORKDIR /app/client-server
#Mount folder to execute
COPY client-server/ /app/client-server
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]
