{{- define "ck-server-containers" -}}
{{- $top := index . 0 -}}
{{- $g := fromJson (include "ck-application.global" $top) -}}
- name: {{ $top.Values.server.faceModel.name }}
  image: {{ template "ck-application.imagePath" (merge (dict "imageName" "ck-face-model") $top) }}
  imagePullPolicy: {{ template "ck-application.imagePullPolicy" $top }}
  ports:    
    {{- if $g.security.tls.enabled }}
    - name: tls-server-svc
      containerPort: {{ $top.Values.server.faceModel.httpsPort }}
    {{- else }}
    - name: http-server-svc
      containerPort: {{ $top.Values.server.faceModel.httpPort }}
    {{- end }}
  resources:
{{- include "ck-application.resources" (index $top.Values "resources" "face-model") | indent 2 }}
  env:
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
  {{- if $g.security.tls.enabled }}
  - name: CERT_PATH
    value: {{ $top.Values.server.secretsPath.certPath }}/tls.crt
  - name: KEY_PATH
    value: {{ $top.Values.server.secretsPath.certPath }}/tls.key
  - name: CA_PATH
    value: {{ $top.Values.server.secretsPath.certPath }}/ca.crt 
  {{- end }}
  - name: TLS_ENABLED
  {{- if $g.security.tls.enabled }}
    value: "true"
  {{- else }}
    value: "false"
  {{- end }}
  volumeMounts:
  {{- if $top.Values.storage.enabled }}
  - name: {{ template "ck-server.name" $top }}-persistent-storage
  {{- else }}
  - name: {{ template "ck-server.name" $top }}-ephemeral-storage
  {{- end }}
    mountPath: /app/build
  {{- if $g.security.tls.enabled }}
  - name: tls-server-cert
    mountPath: {{ $top.Values.server.secretsPath.certPath }}
    readOnly: true
  {{- end }}
volumes:
{{- if $top.Values.storage.enabled }}
- name: {{ template "ck-server.name" $top }}-persistent-storage
  persistentVolumeClaim:
    claimName: {{ template "ck-server.name" $top }}-pv-claim
{{- else }}
- name: {{ template "ck-server.name" $top }}-ephemeral-storage
  emptyDir: {}
{{- end }}
{{- if $g.security.tls.enabled }}
- name: tls-server-cert
  secret:
    secretName: {{ template "ck-server.name" $top }}-cert
{{- end }}
{{- end -}}