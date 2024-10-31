ARG VERSION=17-oracle
FROM openjdk:$VERSION

ENV JAVA_OPTS=""

#Mount jar target file
COPY --chmod=0755 --chown=0:0  *.jar /api-server/app.jar
COPY --chmod=0755 --chown=0:0 application.yaml /api-server/application.yaml

# Ensure application.yaml can be provided via a ConfigMap
ENV CONFIG_PATH="/api-server/application.yaml"

VOLUME [ "/api-server" ]

ARG COMMIT
ARG APP_VERSION
ARG BUILD_TIME

LABEL \
    ck.app.commit=$COMMIT \
    ck.app.version=$APP_VERSION \
    ck.image.title="CK API Authentication" \
    ck.image.created="$BUILD_TIME"

EXPOSE 8080

# Entry point for the Spring Boot application, includes dynamic loading of the keystore and config
ENTRYPOINT [ "sh", "-c", "java $JAVA_OPTS -Djava.security.egd=file:/dev/./urandom \
  -Dspring.config.location=$CONFIG_PATH \
  -jar /api-server/app.jar"]