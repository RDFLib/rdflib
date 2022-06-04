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

exit_handler() {
    1>&2 declare -p fuseki_pid_normal fuseki_pid_tdb
    if [ -z "${FUSEKI_SKIP_SHUTDOWN}" ]
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
    if [ -n "${FUSEKI_DUMP_FULL_LOGS}" ]
    then
        dump_cmd=(cat)
    else
        dump_cmd=(tail -15)
    fi

    if [ -n "${FUSEKI_DUMP_LOGS}" ] || [ "${xrc}" != "0" ]
    then
        1>&2 echo "dumping fuseki_log_normal=${fuseki_log_normal}"
        "${dump_cmd[@]}" "${fuseki_log_normal}" || :
        1>&2 echo "dumping fuseki_log_tdb=${fuseki_log_tdb}"
        "${dump_cmd[@]}"  "${fuseki_log_tdb}" || :
    fi
}


main() {
    : "${LOCALSTATEDIR:=${script_dirname}/var}"
    # : ${FUSEKI_PORT:=3030}
    : "${XDG_CACHE_HOME:=${HOME}/.cache}"

    local jena_uri="https://archive.apache.org/dist/jena/binaries/apache-jena-fuseki-3.17.0.tar.gz"
    local jena_sha512="2b92f3304743da335f648c1be7b5d7c3a94725ed0a9b5123362c89a50986690114dcef0813e328126b14240f321f740b608cc353417e485c9235476f059bd380"
    local jena_archive_basename
    jena_archive_basename="$(basename "${jena_uri}")"
    local jena_archive="${XDG_CACHE_HOME}/${jena_archive_basename}"
    local jena_stem="${jena_archive_basename%%.tar.gz}"

    1>&2 declare -p jena_uri jena_archive XDG_CACHE_HOME LOCALSTATEDIR
    if ! [ -e "${jena_archive}" ]
    then
        mkdir -vp "${XDG_CACHE_HOME}"
        curl "${jena_uri}" -o "${jena_archive}"
    fi
    printf "%s  %s\n" "${jena_sha512}" "${jena_archive_basename}" > "${jena_archive}.sha512"
    (cd "${XDG_CACHE_HOME}" && shasum -c -a512 "${jena_archive_basename}.sha512") || {
        echo 1>&2 "ERROR: digest verification failed"
        rm -rv "${jena_archive}" "${jena_archive}.sha512"
    }
    mkdir -vp "${LOCALSTATEDIR}"
    tar -zxf "${jena_archive}" -C "${LOCALSTATEDIR}"

    local FUSEKI_HOME=${LOCALSTATEDIR}/${jena_stem}
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
    FUSEKI_BASE="${fuseki_base_tdb}" bash "${FUSEKI_HOME}/fuseki-server" \
        --port "${fuseki_port_tdb}" --debug \
        --update --memTDB --set tdb:unionDefaultGraph=true /db &>"${fuseki_log_tdb}" &
    fuseki_pid_tdb="${!}"
    echo "${fuseki_pid_tdb}" > "${fuseki_pidfile_tdb}"

    1>&2 declare -p fuseki_pid_tdb fuseki_pid_normal

    wait_http_okay "pid=${fuseki_pid_normal}" "url=http://localhost:${fuseki_port_normal}/" "label=fuseki-normal"
    wait_http_okay "pid=${fuseki_pid_tdb}" "url=http://localhost:${fuseki_port_tdb}/" "label=fuseki-tdb"

    assert_pid_running "pid=${fuseki_pid_tdb}" "label=fuseki-tdb"
    assert_pid_running "pid=${fuseki_pid_normal}" "label=fuseki-normal"

    local -a args=("${@}")

    1>&2 echo "running: ${args[*]}"

    local xrc=1
    "${args[@]}"; xrc="${?}"
    exit "${xrc}"
}

main "${@}"
