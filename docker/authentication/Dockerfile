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

# Mount the Spring Boot JAR file
COPY --chmod=0755 --chown=0:0  *.jar app.jar

# Expose port 8443 for HTTPS
EXPOSE 8443

# Create a volume for the /api-server directory (optional, for external files)
VOLUME [ "/api-server" ]

# Ensure that keystore can be dynamically injected via Kubernetes or environment variable
ENV KEYSTORE_PATH="/run/secrets/keystore/keystore.p12"
ENV KEYSTORE_PASSWORD=""

# Ensure application.yaml can be provided via a ConfigMap
ENV CONFIG_PATH="/etc/config/application.yaml"

# Entry point for the Spring Boot application, includes dynamic loading of the keystore and config
ENTRYPOINT [ "sh", "-c", "java $JAVA_OPTS -Djava.security.egd=file:/dev/./urandom \
  -Dspring.config.location=$CONFIG_PATH \
  -Dserver.ssl.key-store=$KEYSTORE_PATH \
  -Dserver.ssl.key-store-password=$KEYSTORE_PASSWORD \
  -Dserver.ssl.key-store-type=PKCS12 \
  -jar /app.jar"]
