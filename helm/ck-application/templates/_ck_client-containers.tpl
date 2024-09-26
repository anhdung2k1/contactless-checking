{{- define "ck-client-containers" -}}
{{- $top := index . 0 -}}
- name: {{ $top.Values.server.faceClient.name }}
  image: {{ include "ck-application.imagePath" (merge (dict "imageName" "ck-face-client") $top) }}
  imagePullPolicy: {{ include "ck-application.imagePullPolicy" $top }}
  env:
    - name: MODEL_URL
      value: {{ include "ck-application.modelCommunication" $top }}
    - name: HOST_IP
      value: {{ include "ck-application.authCommunication" $top }}
  ports:
    - name: http-client-svc
      containerPort: {{ $top.Values.server.faceClient.httpPort }}
    - name: tls-client-svc
      containerPort: {{ $top.Values.server.faceClient.tlsPort }}
  resources:
    {{- include "ck-application.resources" (index $top.Values "resources" "face-client") | indent 2 }}
  volumeMounts:
  - name: tls-client-cert
    mountPath: {{ $top.Values.server.secretsPath.certPath }}
    readOnly: true
  - name: nginx-conf
    mountPath: /etc/nginx/conf.d/
volumes:
- name: nginx-conf
  configMap:
    name: {{ template "ck-client.name" $top }}-configmap
    items:
      - key: default.conf
        path: default.conf
- name: tls-client-cert
  secret:
    secretName: tls-cert
{{- end -}}