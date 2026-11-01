#!/usr/bin/env bash

# script_name="${0}"
script_dirname="$( dirname -- "${0}" )"
# script_basename="$( basename -- "${0}" )"

set -eo pipefail

wait_http_okay() {
    local timeout=30
    for var in "${@}"
    do
        eval "local ${var}"
    done
    1>&2 echo "INFO: checking if ${url} (${label}) is okay"
    for ((i=1;i<=${timeout};i++))
    do
        curl --silent "${url}" --fail -o /dev/null && {
            1>&2 echo "INFO: url ${url} (${label}) is okay"
            return 0
        }
        kill -0 "${pid}" 2>/dev/null 1>&2 || {
            1>&2 echo "ERROR: pid ${pid} (${label}) not running anymore, see log dump below for the possible cause."
            return 1
        }
        1>&2 echo "INFO: url ${url} (${label}) not okay, waiting ..."
        sleep 2
    done
    1>&2 echo "ERROR: timed out trying to load ${url} (${label}), see log dump below for the possible cause."
    return 1
}

assert_pid_running() {
    for var in "${@}"
    do
        eval "local ${var}"
    done

    kill -0 "${pid}" 2>/dev/null 1>&2 || {
        1>&2 echo "ERROR: pid ${pid} (${label}) not running anymore, see log dump below for the possible cause."
        return 1
    }
    1>&2 echo "INFO: pid ${pid} (${label}) running"
    return 0
}

kill_and_wait_pid() {
    local timeout=10
    for var in "${@}"
    do
        eval "local ${var}"
    done
    1>&2 echo "INFO: killing pid ${pid} (${label})"
    kill "${pid}"
    for ((i=1;i<=${timeout};i++))
    do
        kill -0 "${pid}" 2>/dev/null 1>&2 || {
            1>&2 echo "INFO: pid ${pid} (${label}) is dead "
            return 0
        }
        1>&2 echo "INFO: pid ${pid} (${label}) is not dead, waiting ..."
        sleep 2
    done
    1>&2 echo "ERROR: wait timeout for pid ${pid} (${label})"
    return 1
}

fuseki_pid_normal=""
fuseki_pid_tdb=""

fuseki_log_normal=""
fuseki_log_tdb=""

xrc=1

exit_handler() {
    1>&2 declare -p fuseki_pid_normal fuseki_pid_tdb
    if [ -z "${FUSEKI_SKIP_SHUTDOWN:-}" ]
    then
        if [ -n "${fuseki_pid_normal}" ]
        then
            kill_and_wait_pid "pid=${fuseki_pid_normal}" "label=fuseki-normal" || :
        fi
        if [ -n "${fuseki_pid_tdb}" ]
        then
            kill_and_wait_pid "pid=${fuseki_pid_tdb}" "label=fuseki-tdb" || :
        fi
    else
        1>&2 echo "WARNING: not killing fuseki fuseki_pid_normal=${fuseki_pid_normal} fuseki_pid_tdb=${fuseki_pid_tdb}"
    fi

    local -a dump_cmd
    if [ -n "${FUSEKI_DUMP_FULL_LOGS:-}" ]
    then
        dump_cmd=(cat)
    else
        dump_cmd=(tail -15)
    fi

    if [ -n "${FUSEKI_DUMP_LOGS:-}" ] || [ "${xrc}" != "0" ]
    then
        if [ -n "${fuseki_log_normal}" ]
        then
            1>&2 echo "dumping fuseki_log_normal=${fuseki_log_normal}"
            "${dump_cmd[@]}" "${fuseki_log_normal}" || :
        fi
        if [ -n "${fuseki_log_tdb}" ]
        then
            1>&2 echo "dumping fuseki_log_tdb=${fuseki_log_tdb}"
            "${dump_cmd[@]}" "${fuseki_log_tdb}" || :
        fi
    fi
}


main() {
    : "${LOCALSTATEDIR:=${script_dirname}/var}"
    # : ${FUSEKI_PORT:=3030}
    : "${XDG_CACHE_HOME:=${HOME}/.cache}"

    local jena_archive_basename="apache-jena-fuseki-6.1.0.tar.gz"
    local jena_uri="https://dlcdn.apache.org/jena/binaries/${jena_archive_basename}"
    local jena_archive_uri="https://archive.apache.org/dist/jena/binaries/${jena_archive_basename}"
    local jena_sha512="75457f45d14397876a41ed51abe7ae5d2f1e708dfe1315765f858158bc5c6813bc036ec1539ddc4dffd26201f5cc31fadec299ca5c3dc2548b723513ed31d326"
    local jena_archive="${XDG_CACHE_HOME}/${jena_archive_basename}"
    local jena_checksum="${jena_archive}.sha512"
    local jena_stem="${jena_archive_basename%%.tar.gz}"

    1>&2 declare -p jena_uri jena_archive_uri jena_archive XDG_CACHE_HOME LOCALSTATEDIR
    if ! [ -e "${jena_archive}" ]
    then
        mkdir -vp "${XDG_CACHE_HOME}"
        curl --fail --location --retry 3 --retry-delay 2 \
            "${jena_uri}" -o "${jena_archive}" || {
            1>&2 echo "WARNING: CDN download failed; trying Apache archive"
            curl --fail --location --retry 3 --retry-delay 2 \
                "${jena_archive_uri}" -o "${jena_archive}"
        }
    fi
    printf "%s  %s\n" "${jena_sha512}" "${jena_archive_basename}" > "${jena_checksum}"
    (cd "${XDG_CACHE_HOME}" && shasum -c -a 512 "$(basename "${jena_checksum}")") || {
        echo 1>&2 "ERROR: digest verification failed"
        rm -v "${jena_archive}" "${jena_checksum}"
        exit 1
    }
    mkdir -vp "${LOCALSTATEDIR}"
    tar -zxf "${jena_archive}" -C "${LOCALSTATEDIR}"

    local FUSEKI_HOME="${LOCALSTATEDIR}/${jena_stem}"
    1>&2 declare -p FUSEKI_HOME
    export FUSEKI_HOME

    fuseki_base_normal="${FUSEKI_HOME}/run-normal"
    fuseki_base_tdb="${FUSEKI_HOME}/run-tdb"
    local fuseki_pidfile_normal="${fuseki_base_normal}/server.pid"
    local fuseki_pidfile_tdb="${fuseki_base_tdb}/server.pid"

    mkdir -vp "${fuseki_base_normal}" "${fuseki_base_tdb}"
    local fuseki_port_normal=3030
    local fuseki_port_tdb=3031

    1>&2 declare -p fuseki_base_normal fuseki_base_tdb fuseki_pidfile_normal fuseki_pidfile_tdb fuseki_port_normal fuseki_port_tdb

    trap exit_handler EXIT

    fuseki_log_normal="${fuseki_base_normal}/out.log"
    fuseki_log_tdb="${fuseki_base_tdb}/out.log"

    1>&2 declare -p fuseki_log_normal fuseki_log_tdb

    1>&2 echo "INFO: starting fuseki: normal"
    FUSEKI_BASE="${fuseki_base_normal}" bash "${FUSEKI_HOME}/fuseki-server" \
        --port "${fuseki_port_normal}" --debug \
        --update --mem /db &>"${fuseki_log_normal}" &
    fuseki_pid_normal="${!}"
    echo "${fuseki_pid_normal}" > "${fuseki_pidfile_normal}"

    1>&2 echo "INFO: starting fuseki: tdb"
    mkdir -vp "${fuseki_base_tdb}/database"
    local fuseki_config_tdb="${fuseki_base_tdb}/config.ttl"
    printf '%s\n' \
        'PREFIX fuseki: <http://jena.apache.org/fuseki#>' \
        'PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>' \
        'PREFIX tdb2:   <http://jena.apache.org/2016/tdb#>' \
        '' \
        '<#service> rdf:type fuseki:Service ;' \
        '    fuseki:name "db" ;' \
        '    fuseki:serviceQuery "query" ;' \
        '    fuseki:serviceQuery "sparql" ;' \
        '    fuseki:serviceUpdate "update" ;' \
        '    fuseki:serviceReadWriteGraphStore "data" ;' \
        '    fuseki:dataset <#dataset> .' \
        '' \
        '<#dataset> rdf:type tdb2:DatasetTDB2 ;' \
        "    tdb2:location \"${fuseki_base_tdb}/database\" ;" \
        '    tdb2:unionDefaultGraph true .' \
        > "${fuseki_config_tdb}"
    FUSEKI_BASE="${fuseki_base_tdb}" bash "${FUSEKI_HOME}/fuseki-server" \
        --port "${fuseki_port_tdb}" --debug \
        --conf "${fuseki_config_tdb}" &>"${fuseki_log_tdb}" &
    fuseki_pid_tdb="${!}"
    echo "${fuseki_pid_tdb}" > "${fuseki_pidfile_tdb}"

    1>&2 declare -p fuseki_pid_tdb fuseki_pid_normal

    wait_http_okay "pid=${fuseki_pid_normal}" "url=http://localhost:${fuseki_port_normal}/" "label=fuseki-normal"
    wait_http_okay "pid=${fuseki_pid_tdb}" "url=http://localhost:${fuseki_port_tdb}/" "label=fuseki-tdb"

    assert_pid_running "pid=${fuseki_pid_tdb}" "label=fuseki-tdb"
    assert_pid_running "pid=${fuseki_pid_normal}" "label=fuseki-normal"

    local -a args=("${@}")

    1>&2 echo "running: ${args[*]}"

    if [ "${#args[@]}" -eq 0 ]
    then
        1>&2 echo "ERROR: no command supplied"
        xrc=2
        return "${xrc}"
    fi

    set +e
    "${args[@]}"
    xrc="${?}"
    set -e

    return "${xrc}"
}

main "${@}"
exit "${xrc}"
