{{- define "ck-client-containers" -}}
{{- $top := index . 0 -}}
- name: {{ $top.Values.server.faceClient.name }}
  image: {{ include "ck-application.imagePath" (merge (dict "imageName" "ck-face-client") $top) }}
  imagePullPolicy: {{ include "ck-application.imagePullPolicy" $top }}
  env:
    - name: MODEL_URL
      value: {{ include "ck-application.authCommunication" $top }}
    - name: HOST_IP
      value: {{ include "ck-application.modelCommunication" $top }}
  ports:
    - name: http-client-svc
      containerPort: {{ $top.Values.server.faceClient.httpPort }}
    - name: tls-client-svc
      containerPort: {{ $top.Values.server.faceClient.tlsPort }}
  resources:
    {{- include "ck-application.resources" (index $top.Values "resources" "face-client") | indent 2 }}
{{- end -}}