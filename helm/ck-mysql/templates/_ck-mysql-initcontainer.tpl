{{- define "ck-mysql.initContainer" -}}
{{- $top := index . 0 }}
{{- $svcName := include "ck-mysql.name" $top }}
{{- $g := fromJson (include "ck-mysql.global" $top) -}}
- name: ck-mysql-initcontainer
  image: {{ template "ck-mysql.imagePath" (merge (dict "imageName" "ck-mysql") $top) }}
  imagePullPolicy: {{ template "ck-mysql.imagePullPolicy" $top }}
  securityContext:
    allowPrivilegeEscalation: false
    privileged: false
    readOnlyRootFilesystem: true
    runAsNonRoot: true
    capabilities:
      drop:
        - ALL
    {{- with (index $top.Values "seccompProfile" "ck-mysql-initcontainer") }}
    seccompProfile:
    {{- toYaml . | nindent 6 }}
    {{- end }}
    command:
    - /bin/bash
    - -c
    - |
      set -ex
      [[ $HOSTNAME =~ ([0-9]+)$ ]] || exit 1
      ordinal=${BASH_REMATCH[1]}
      echo [mysqld] > /mnt/conf.d/server-id.cnf
      # Add an offset to avoid reserved server-id=0 value.
      echo server-id=$((100 + $ordinal)) >> /mnt/conf.d/server-id.cnf
      # Copy appropriate conf.d files from config-map to emptyDir.
      if [[ $ordinal -eq 0 ]]; then
      cp /mnt/config-map/primary.cnf /mnt/conf.d/
      else
      cp /mnt/config-map/replica.cnf /mnt/conf.d/
      fi
    resources:
{{- include "ck-mysql.resources" (index $top.Values "resources" "ck-initcontainer") | indent 2 }}
    volumeMounts:
    - name: conf
      mountPath: /mnt/conf.d
    - name: config-map
      mountPath: /mnt/config-map
{{- end }}