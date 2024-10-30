{{- define "ck-mysql.container" -}}
{{- $top := index . 0 -}}
- name: {{ $top.Values.server.mysqlServer.name }}
  image: {{ template "ck-application.imagePath" (merge (dict "imageName" "ck-mysql") $top) }}
  imagePullPolicy: {{ template "ck-application.imagePullPolicy" $top }}
  securityContext:
    {{- include "ck-application.appArmorProfile.securityContext" (list $top "mysql") | indent 4 }}
    allowPrivilegeEscalation: false
    privileged: false
    readOnlyRootFilesystem: false
    runAsNonRoot: false
    {{- with (index $top.Values "seccompProfile" "mysql") }}
    seccompProfile:
    {{- toYaml . | nindent 6 }}
    {{- end }}
  env:
  - name: MYSQL_PASSWORD
    valueFrom:
      secretKeyRef:
          name: {{ template "ck-mysql.name" $top }}-secret
          key: {{ template "ck-mysql.name" $top }}-password
  - name: MYSQL_ROOT_PASSWORD
    valueFrom:
      secretKeyRef:
          name: {{ template "ck-mysql.name" $top }}-secret
          key: {{ template "ck-mysql.name" $top }}-root-password
  {{- if not (eq ((include "ck-mysql.password" $top) | b64dec) "root") }}
  - name: MYSQL_USER
    valueFrom:
      secretKeyRef:
          name: {{ template "ck-mysql.name" $top }}-secret
          key: {{ template "ck-mysql.name" $top }}-user
  {{- end }}
  - name: MYSQL_DATABASE
    valueFrom:
      secretKeyRef:
          name: {{ template "ck-mysql.name" $top }}-secret
          key: {{ template "ck-mysql.name" $top }}-dbName
  ports:
  - containerPort: {{ $top.Values.server.mysqlServer.port }}
  volumeMounts:
  {{- if $top.Values.storage.enabled }}
  - name: {{ template "ck-mysql.name" $top }}-persistent-storage
  {{- else }}
  - name: {{ template "ck-mysql.name" $top }}-ephemeral-storage
  {{- end }}
    mountPath: /var/lib/mysql
  - name: conf
    mountPath: /etc/mysql/conf.d
  resources:
{{- include "ck-application.resources" (index $top.Values "resources" "mysql") | indent 2 }}
- name: {{ $top.Values.server.xtrabackup.name }}
  image: {{ template "ck-application.imagePath" (merge (dict "imageName" "ck-xtrabackup") $top) }}
  imagePullPolicy: {{ template "ck-application.imagePullPolicy" $top }}
  securityContext:
    {{- include "ck-application.appArmorProfile.securityContext" (list $top "mysql") | indent 4 }}
    allowPrivilegeEscalation: false
    privileged: false
    readOnlyRootFilesystem: false
    runAsNonRoot: false
    {{- with (index $top.Values "seccompProfile" "mysql") }}
    seccompProfile:
    {{- toYaml . | nindent 6 }}
    {{- end }}
  ports:
  - name: {{ $top.Values.server.xtrabackup.name }}
    containerPort: {{ $top.Values.server.xtrabackup.port }}
  command:
  - bash
  - "-c"
  - |
    set -ex
    cd /var/lib/mysql

    # Determine binlog position of cloned data, if any.
    if [[ -f xtrabackup_slave_info && "x$(<xtrabackup_slave_info)" != "x" ]]; then
    # XtraBackup already generated a partial "CHANGE MASTER TO" query
    # because we're cloning from an existing replica. (Need to remove the tailing semicolon!)
    cat xtrabackup_slave_info | sed -E 's/;$//g' > change_master_to.sql.in
    # Ignore xtrabackup_binlog_info in this case (it's useless).
    rm -f xtrabackup_slave_info xtrabackup_binlog_info
    elif [[ -f xtrabackup_binlog_info ]]; then
    # We're cloning directly from primary. Parse binlog position.
    [[ `cat xtrabackup_binlog_info` =~ ^(.*?)[[:space:]]+(.*?)$ ]] || exit 1
    rm -f xtrabackup_binlog_info xtrabackup_slave_info
    echo "CHANGE MASTER TO MASTER_LOG_FILE='${BASH_REMATCH[1]}',\
            MASTER_LOG_POS=${BASH_REMATCH[2]}" > change_master_to.sql.in
    fi

    # Check if we need to complete a clone by starting replication.
    if [[ -f change_master_to.sql.in ]]; then
    echo "Waiting for mysqld to be ready (accepting connections)"
    until mysql -h 127.0.0.1 -u $MYSQL_USER -p$MYSQL_PASSWORD -e "SELECT 1"; do sleep 1; done

    echo "Initializing replication from clone position"
    mysql -h 127.0.0.1 \
            -e "$(<change_master_to.sql.in), \
                    MASTER_HOST='mysql-0.mysql', \
                    MASTER_USER="$MYSQL_USER", \
                    MASTER_PASSWORD="$MYSQL_PASSWORD", \
                    MASTER_CONNECT_RETRY=10; \
                START SLAVE;" || exit 1
    # In case of container restart, attempt this at-most-once.
    mv change_master_to.sql.in change_master_to.sql.orig
    fi

    # Start a server to send backups when requested by peers.
    exec ncat --listen --keep-open --send-only --max-conns=1 3307 -c \
    "xtrabackup --backup --slave-info --stream=xbstream --host=127.0.0.1 --user=$MYSQL_USER"
  volumeMounts:
  {{- if $top.Values.storage.enabled }}
  - name: {{ template "ck-mysql.name" $top }}-persistent-storage
  {{- else }}
  - name: {{ template "ck-mysql.name" $top }}-ephemeral-storage
  {{- end }}
    mountPath: /var/lib/mysql
  - name: conf
    mountPath: /etc/mysql/conf.d
  resources:
{{- include "ck-application.resources" (index $top.Values "resources" "xtrabackup") | indent 2 }}
volumes:
- name: conf
  emptyDir: {}
- name: config-map
  configMap:
    name: {{ template "ck-mysql.name" $top }}-configmap
{{- if $top.Values.storage.enabled }}
- name: {{ template "ck-mysql.name" $top }}-persistent-storage
  persistentVolumeClaim:
    claimName: {{ template "ck-mysql.name" $top }}-pv-claim
{{- else }}
- name: {{ template "ck-mysql.name" $top }}-ephemeral-storage
  emptyDir: {}
{{- end }}
{{- end }}