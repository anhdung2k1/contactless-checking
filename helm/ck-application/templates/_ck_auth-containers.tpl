{{- define "ck-auth-containers" -}}
{{- $top := index . 0 -}}
- name: {{ $top.Values.server.authentication.name }}
  image: {{ template "ck-application.imagePath" (merge (dict "imageName" "ck-authentication") $top) }}
  imagePullPolicy: {{ template "ck-application.imagePullPolicy" $top }}
  ports:
    - name: https-auth-svc
      containerPort: {{ $top.Values.server.authentication.port }}
  resources:
{{- include "ck-application.resources" (index $top.Values "resources" "authentication") | indent 2 }}
  env:
  - name: DB_HOST
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-mysql.name" $top }}-secret
        key: {{ template "ck-mysql.name" $top }}-host
  - name: DB_NAME
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-mysql.name" $top }}-secret
        key: {{ template "ck-mysql.name" $top }}-dbName
  - name: DB_USERNAME
  {{- if not (eq ((include "ck-mysql.password" $top) | b64dec) "root") }}
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-mysql.name" $top }}-secret
        key: {{ template "ck-mysql.name" $top }}-user
  {{- else }}
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-mysql.name" $top }}-secret
        key: {{ template "ck-mysql.name" $top }}-root-password
  {{- end }}
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-mysql.name" $top }}-secret
        key: {{ template "ck-mysql.name" $top }}-password
  - name: KEYSTORE_PASSWORD
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-authentication.name" $top }}-secret
        key: {{ template "ck-authentication.name" $top }}-keystore-password
  - name: JWT_KEY
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-authentication.name" $top }}-secret
        key: {{ template "ck-authentication.name" $top }}-jwt-key
  - name: AWS_ACCESS_KEY_ID
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-authentication.name" $top }}-secret
        key: {{ template "ck-authentication.name" $top }}-aws-key
  - name: AWS_SECRET_ACCESS_KEY
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-authentication.name" $top }}-secret
        key: {{ template "ck-authentication.name" $top }}-aws-secret
  - name: AWS_DEFAULT_REGION
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-authentication.name" $top }}-secret
        key: {{ template "ck-authentication.name" $top }}-aws-region
  - name: KEYSTORE_PATH
    value: {{ $top.Values.server.secretsPath.keyStorePath }}/keystore.p12
  - name: CONFIG_PATH
    value: /etc/config/application.yaml
  volumeMounts:
  - name: config-properties
    mountPath: /etc/config
  - name: keystore-cert
    mountPath: {{ $top.Values.server.secretsPath.keyStorePath }}
    subPath: keystore.p12
volumes:
- name: config-properties
  configMap:
    name: {{ template "ck-authentication.name" $top }}-configmap
    items:
      - key: application.yaml
        path: application.yaml
- name: keystore-cert
  persistentVolumeClaim:
    claimName: {{ template "ck-authentication.name" $top }}-pv-claim
{{- end -}}