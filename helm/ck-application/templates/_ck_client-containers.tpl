{{- define "ck-client-containers" -}}
{{- $top := index . 0 -}}
{{- $g := fromJson (include "ck-application.global" $top) -}}
- name: {{ $top.Values.server.faceClient.name }}
  image: {{ include "ck-application.imagePath" (merge (dict "imageName" "ck-face-client") $top) }}
  imagePullPolicy: {{ include "ck-application.imagePullPolicy" $top }}
  securityContext:
    {{- include "ck-application.appArmorProfile.securityContext" (list $top "face-client") | indent 4 }}
    allowPrivilegeEscalation: false
    privileged: false
    readOnlyRootFilesystem: false
    runAsNonRoot: false
    {{- with (index $top.Values "seccompProfile" "face-client") }}
    seccompProfile:
    {{- toYaml . | nindent 6 }}
    {{- end }}
  env:
  # The fetch client used external IP from LoadBalancer/NodePort or Ingress. Not working with ClusterIP
  - name: MODEL_URL
    value: {{ include "ck-application.connection" (list $top (include "ck-server.name" $top)) }}
  - name: HOST_IP
    value: {{ include "ck-application.connection" (list $top (include "ck-authentication.name" $top)) }}
  ports:    
    {{- if $g.security.tls.enabled }}
    - name: tls-client-svc
      containerPort: {{ $top.Values.server.faceClient.httpsPort }}
    {{- else }}
    - name: http-client-svc
      containerPort: {{ $top.Values.server.faceClient.httpPort }}
    {{- end }}
  resources:
{{- include "ck-application.resources" (index $top.Values "resources" "face-client") | indent 2 }}
  volumeMounts:
  - name: nginx-conf
    mountPath: /etc/nginx/conf.d/
  {{- if $g.security.tls.enabled }}
  - name: tls-client-cert
    mountPath: {{ $top.Values.server.secretsPath.certPath }}
    readOnly: true
  {{- end }}
volumes:
- name: nginx-conf
  configMap:
    name: {{ template "ck-client.name" $top }}-configmap
    items:
      - key: default.conf
        path: default.conf
{{- if $g.security.tls.enabled }}
- name: tls-client-cert
  secret:
    secretName: {{ template "ck-client.name" $top }}-cert
{{- end }}
{{- end -}}