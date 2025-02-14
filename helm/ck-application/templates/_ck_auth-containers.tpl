{{- define "ck-auth-containers" -}}
{{- $top := index . 0 -}}
{{- $g := fromJson (include "ck-application.global" $top) -}}
- name: {{ $top.Values.server.authentication.name }}
  image: {{ template "ck-application.imagePath" (merge (dict "imageName" "ck-authentication") $top) }}
  imagePullPolicy: {{ template "ck-application.imagePullPolicy" $top }}
  securityContext:
    {{- include "ck-application.appArmorProfile.securityContext" (list $top "authentication") | indent 4 }}
    allowPrivilegeEscalation: false
    privileged: false
    readOnlyRootFilesystem: false
    runAsNonRoot: false
    capabilities:
      drop:
        - ALL
    {{- with (index $top.Values "seccompProfile" "authentication") }}
    seccompProfile:
    {{- toYaml . | nindent 6 }}
    {{- end }}
  ports:
    {{- if $g.security.tls.enabled }}
    - name: tls-auth-svc
      containerPort: {{ $top.Values.server.authentication.httpsPort }}
    {{- else }}
    - name: http-auth-svc
      containerPort: {{ $top.Values.server.authentication.httpPort }}
    {{- end }}
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
  - name: CONFIG_PATH
    value: /etc/config/application.yaml
  {{- if $g.security.tls.enabled }}
  - name: KEYSTORE_PASSWORD
    valueFrom:
      secretKeyRef:
        name: {{ template "ck-authentication.name" $top }}-secret
        key: {{ template "ck-authentication.name" $top }}-keystore-password
  - name: KEYSTORE_PATH
    value: {{ $top.Values.server.secretsPath.keyStorePath }}/keystore.p12
  {{- end }}
  volumeMounts:
  - name: config-properties
    mountPath: /etc/config
  {{- if $g.security.tls.enabled }}
  - name: keystore-cert
    mountPath: {{ $top.Values.server.secretsPath.keyStorePath }}
  {{- end }}
{{ include "ck-application.readinessProbe" (list $top "/actuator/health" "authentication") | indent 2 }}
{{ include "ck-application.livenessProbe" (list $top "/actuator/health" "authentication") | indent 2 }}
volumes:
- name: config-properties
  configMap:
    name: {{ template "ck-authentication.name" $top }}-configmap
    items:
      - key: application.yaml
        path: application.yaml
{{- if $g.security.tls.enabled }}
- name: tls-auth-secret
  secret:
    secretName: {{ template "ck-application.name" $top }}-cert
- name: keystore-cert
  {{- if $top.Values.storage.enabled }}
  persistentVolumeClaim:
    claimName: {{ template "ck-authentication.name" $top }}-pv-claim
  {{- else }}
  emptyDir: {}
  {{- end }}
{{- end }}
{{- end -}}
