#!/usr/bin/env bash
# Overlay on the shared webmin-lab:2.670 image: real Postfix plus a
# postfix-module user whose ACL has general=0 and startstop=0.
set -euo pipefail

WEBMIN_CONF=/etc/webmin
POSTFIX_MOD="${WEBMIN_CONF}/postfix"
ACL_FILE="${POSTFIX_MOD}/limited.acl"
DEFAULT_ACL=/usr/share/webmin/postfix/defaultacl
USERS_FILE="${WEBMIN_CONF}/miniserv.users"
WEBMIN_ACL="${WEBMIN_CONF}/webmin.acl"
LIMITED_USER=limited
LIMITED_PASS=lablimited

ensure_postfix() {
  if ! command -v postconf >/dev/null 2>&1 || ! command -v postfix >/dev/null 2>&1; then
    apt-get update
    echo "postfix postfix/main_mailer_type select Local only" | debconf-set-selections
    echo "postfix postfix/mailname string lab.local" | debconf-set-selections
    apt-get install -y --no-install-recommends postfix
  fi
  mkdir -p /etc/postfix /var/spool/postfix
  postconf -e inet_protocols=ipv4
  postconf -e inet_interfaces=loopback-only
  postconf -e myhostname=webminh11.lab.local
  mkdir -p "${POSTFIX_MOD}"
  if [[ -f "${POSTFIX_MOD}/config" ]]; then
    sed -i '/^reload_cmd=/d;/^start_cmd=/d;/^stop_cmd=/d' "${POSTFIX_MOD}/config"
    {
      echo "reload_cmd=/usr/sbin/postfix reload"
      echo "start_cmd=/usr/sbin/postfix start"
      echo "stop_cmd=/usr/sbin/postfix stop"
    } >> "${POSTFIX_MOD}/config"
  fi
  postfix start >/tmp/postfix-start.log 2>&1 || true
  postfix check >/tmp/postfix-check.log 2>&1 || true
}

ensure_limited_user() {
  local hash
  hash="$(perl -e 'print crypt($ARGV[0], q($6$webminh11salt$))' "${LIMITED_PASS}")"
  if [[ -z "${hash}" || "${hash}" == "${LIMITED_PASS}" || "${hash}" == *"*"* ]]; then
    echo "limited-crypt-failed" >&2
    exit 1
  fi
  if ! grep -q "^${LIMITED_USER}:" "${USERS_FILE}"; then
    echo "${LIMITED_USER}:${hash}:0" >> "${USERS_FILE}"
  fi
  if grep -q "^${LIMITED_USER}:" "${WEBMIN_ACL}"; then
    sed -i "s|^${LIMITED_USER}:.*|${LIMITED_USER}: postfix|" "${WEBMIN_ACL}"
  else
    echo "${LIMITED_USER}: postfix" >> "${WEBMIN_ACL}"
  fi
  if [[ -f "${DEFAULT_ACL}" ]]; then
    cp "${DEFAULT_ACL}" "${ACL_FILE}"
  else
    printf 'dir=/\n' > "${ACL_FILE}"
  fi
  if grep -q '^general=' "${ACL_FILE}"; then
    sed -i 's/^general=.*/general=0/' "${ACL_FILE}"
  else
    echo 'general=0' >> "${ACL_FILE}"
  fi
  if grep -q '^startstop=' "${ACL_FILE}"; then
    sed -i 's/^startstop=.*/startstop=0/' "${ACL_FILE}"
  else
    echo 'startstop=0' >> "${ACL_FILE}"
  fi
  grep -q '^dir=' "${ACL_FILE}" || echo 'dir=/' >> "${ACL_FILE}"
  chmod 600 "${USERS_FILE}" "${WEBMIN_ACL}" "${ACL_FILE}"
}

ensure_miniserv_loopback() {
  if [[ -f "${WEBMIN_CONF}/miniserv.conf" ]]; then
    grep -q '^no_testing_cookie=' "${WEBMIN_CONF}/miniserv.conf" \
      || echo 'no_testing_cookie=1' >> "${WEBMIN_CONF}/miniserv.conf"
    grep -q '^ssl_enforce=' "${WEBMIN_CONF}/miniserv.conf" \
      && sed -i 's/^ssl_enforce=.*/ssl_enforce=0/' "${WEBMIN_CONF}/miniserv.conf" \
      || echo 'ssl_enforce=0' >> "${WEBMIN_CONF}/miniserv.conf"
  fi
}

ensure_postfix
ensure_limited_user
ensure_miniserv_loopback

exec /usr/bin/perl /usr/share/webmin/miniserv.pl --nofork /etc/webmin/miniserv.conf
