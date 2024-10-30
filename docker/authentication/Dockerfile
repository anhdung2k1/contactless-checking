ARG VERSION=17-oracle
FROM openjdk:$VERSION

ENV JAVA_OPTS=""

VOLUME [ "/api-server" ]

#Mount jar target file  
COPY --chmod=0755 --chown=0:0  *.jar /api-server/app.jar
COPY --chmod=0755 --chown=0:0 application.yaml /api-server/application.yaml

EXPOSE 8080
# Ensure application.yaml can be provided via a ConfigMap
ENV CONFIG_PATH="/api-server/application.yaml"

ARG COMMIT
ARG APP_VERSION
ARG BUILD_TIME

LABEL \
    ck.app.commit=$COMMIT \
    ck.app.version=$APP_VERSION \
    ck.image.title="CK API Server" \
    ck.image.created="$BUILD_TIME"

ARG USER_ID
RUN echo "${USER_ID}:x:${USER_ID}:${USER_ID}:Identity for ck-application-server:/nonexistent:/bin/false" >> /etc/passwd && \
    echo "${USER_ID}:!::0:::::" >> /etc/shadow

USER ${USER_ID}

# Entry point for the Spring Boot application, includes dynamic loading of the keystore and config
ENTRYPOINT [ "sh", "-c", "java $JAVA_OPTS -Djava.security.egd=file:/dev/./urandom \
  -Dspring.config.location=$CONFIG_PATH \
  -jar /api-server/app.jar"]