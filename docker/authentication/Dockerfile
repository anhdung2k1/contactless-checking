ARG VERSION=17-oracle
FROM openjdk:$VERSION

ENV JAVA_OPTS=""

ARG COMMIT
ARG APP_VERSION
ARG BUILD_TIME

LABEL \
    ck.app.commit=$COMMIT \
    ck.app.version=$APP_VERSION \
    ck.image.title="CK API Server" \
    ck.image.created="$BUILD_TIME"

#Mount jar target file  
COPY --chmod=0755 --chown=0:0  *.jar app.jar

EXPOSE 8443
VOLUME [ "/api-server" ]
ENTRYPOINT [ "sh", "-c", "java $JAVA_OPTS -Djava.security.egd=file:/dev/./urandom -jar /app.jar"]
