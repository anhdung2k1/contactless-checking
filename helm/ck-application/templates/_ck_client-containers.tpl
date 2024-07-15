{{- define "ck-client-containers" -}}
{{- $top := index . 0 -}}
{{- $modelURL := printf "http://%s:%s" $top.Values.server.externalIP $top.Values.server.faceModel.port -}}
{{- $hostIP := printf "http://%s:%s" $top.Values.server.externalIP $top.Values.server.authentication.port -}}
- name: {{ $top.Values.server.faceClient.name }}
  image: {{ include "ck-application.imagePath" (merge (dict "imageName" "ck-face-client") $top) }}
  imagePullPolicy: {{ include "ck-application.imagePullPolicy" $top }}
  env:
    - name: MODEL_URL
      value: {{ $modelURL }}
    - name: HOST_IP
      value: {{ $hostIP }}
  ports:
    - containerPort: {{ $top.Values.server.faceClient.port }}
  resources:
    {{- include "ck-application.resources" (index $top.Values "resources" "face-client") | indent 2 }}
{{- end -}}