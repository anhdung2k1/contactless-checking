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
COPY --chmod=0755 --chown=0:0 application.yaml /etc/config/application.yaml

EXPOSE 8443
# Ensure application.yaml can be provided via a ConfigMap
ENV CONFIG_PATH="/etc/config/application.yaml"

# Entry point for the Spring Boot application, includes dynamic loading of the keystore and config
ENTRYPOINT [ "sh", "-c", "java $JAVA_OPTS -Djava.security.egd=file:/dev/./urandom \
  -Dspring.config.location=$CONFIG_PATH \
  -jar /app.jar"]