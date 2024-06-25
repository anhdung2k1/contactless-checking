{{- define "ck-mysql.initContainer" -}}
{{- $top := index . 0 }}
- name: ck-mysql-initcontainer
  image: {{ template "ck-application.imagePath" (merge (dict "imageName" "ck-mysql") $top) }}
  imagePullPolicy: {{ template "ck-application.imagePullPolicy" $top }}
  securityContext:
    allowPrivilegeEscalation: false
    privileged: false
    readOnlyRootFilesystem: true
    runAsNonRoot: false
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
{{- include "ck-application.resources" (index $top.Values "resources" "initcontainer") | indent 2 }}
  volumeMounts:
  - name: conf
    mountPath: /mnt/conf.d
  - name: config-map
    mountPath: /mnt/config-map
- name: clone-mysql
  image: {{ template "ck-application.imagePath" (merge (dict "imageName" "ck-xtrabackup") $top) }}
  imagePullPolicy: {{ template "ck-application.imagePullPolicy" $top }}
  command:
  - bash
  - "-c"
  - |
    set -ex
    # Skip the clone if data already exists.
    [[ -d /var/lib/mysql/mysql ]] && exit 0
    # Skip the clone on primary (ordinal index 0).
    [[ `hostname` =~ -([0-9]+)$ ]] || exit 1
    ordinal=${BASH_REMATCH[1]}
    [[ $ordinal -eq 0 ]] && exit 0
    # Clone data from previous peer.
    ncat --recv-only mysql-$(($ordinal-1)).mysql 3307 | xbstream -x -C /var/lib/mysql
    # Prepare the backup.
    xtrabackup --prepare --target-dir=/var/lib/mysql
  resources:
{{- include "ck-application.resources" (index $top.Values "resources" "xtrabackup") | indent 2 }}
  volumeMounts:
  - name: {{ template "ck-mysql.name" $top }}-persistent-storage
    mountPath: /var/lib/mysql
  - name: conf
    mountPath: /etc/mysql/conf.d
{{- end }}