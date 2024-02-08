FROM openjdk:17-oracle

ENV JAVA_OPTS=""

ARG COMMIT
ARG APP_VERSION
ARG BUILD_TIME

LABEL \
    ck.app.commit=$COMMIT \
    ck.app.version=$APP_VERSION \
    ck.image.title="CK API Server" \
    ck.image.created="$BUILD_TIME"
    
ADD *.jar app.jar

EXPOSE 8080
VOLUME [ "/api-server" ]
ENTRYPOINT [ "sh", "-c", "java $JAVA_OPTS -Djava.security.egd=file:/dev/./urandom -jar /app.jar"]
