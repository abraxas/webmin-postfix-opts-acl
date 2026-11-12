#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-webminh11}"
export PYTHONUNBUFFERED=1

LABEL="WEBMIN-H11-POSTFIX-ACL"
WITNESS="WEBMIN-H11-POSTFIX-ACL"
IMAGE="webmin-lab:2.670"
LOCK="/tmp/webmin-lab-image.lock"
BASE="http://127.0.0.1:18500"
PIN="3a2b2b8671c0669c129f5275b3dd1853106ae02b"
PIN_TAG="2.670"
REPO_URL="${WEBMIN_SRC_URL:-https://github.com/webmin/webmin.git}"
PIN_DIR="${PWD}/src"

down() {
  echo "== docker compose down -v =="
  docker compose -p "${COMPOSE_PROJECT_NAME}" down -v --remove-orphans || true
}

fail_setup() {
  local reason="$1"
  echo "FAIL ${LABEL} ${reason} ${WITNESS}" | tee poc-last-run.txt
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 webmin || true
  down
  exit 1
}

clone_pin() {
  local got
  if [[ -d "${PIN_DIR}/.git" ]]; then
    got="$(git -C "${PIN_DIR}" rev-parse HEAD)"
    if [[ "${got}" == "${PIN}" ]]; then
      echo "IOC pin-present ${PIN}"
      return 0
    fi
    echo "IOC pin-reclone got=${got} expect=${PIN}"
    rm -rf "${PIN_DIR}"
  fi
  echo "== git clone ${REPO_URL} ${PIN} =="
  GIT_TERMINAL_PROMPT=0 git clone --filter=blob:none --no-checkout "${REPO_URL}" "${PIN_DIR}" \
    || fail_setup "clone-failed"
  GIT_TERMINAL_PROMPT=0 git -C "${PIN_DIR}" fetch --depth 1 origin "${PIN}" \
    || fail_setup "fetch-failed"
  git -C "${PIN_DIR}" checkout --detach FETCH_HEAD || fail_setup "checkout-failed"
  got="$(git -C "${PIN_DIR}" rev-parse HEAD)"
  if [[ "${got}" != "${PIN}" ]]; then
    fail_setup "pin-mismatch"
  fi
  if [[ ! -f "${PIN_DIR}/version" ]] || [[ "$(tr -d '[:space:]' < "${PIN_DIR}/version")" != "${PIN_TAG}" ]]; then
    fail_setup "version-mismatch"
  fi
  echo "IOC pin-ok tag=${PIN_TAG} sha=${got}"
}

ensure_image() {
  python3 - "${LOCK}" "${IMAGE}" "${PWD}/Dockerfile" "${PIN_DIR}" "${PIN_TAG}" <<'PY'
import fcntl
import os
import subprocess
import sys
import tempfile

lock_path, image, dockerfile, src, pin_tag = sys.argv[1:6]
fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o666)
fcntl.flock(fd, fcntl.LOCK_EX)
try:
    inspect = subprocess.run(
        ["docker", "image", "inspect", image],
        capture_output=True,
        check=False,
    )
    if inspect.returncode == 0:
        print(f"IOC image-present {image}", flush=True)
        raise SystemExit(0)
    if not os.path.isfile(os.path.join(src, "setup.sh")):
        print(f"webmin-src-missing {src}", flush=True)
        raise SystemExit(1)
    version_path = os.path.join(src, "version")
    if not os.path.isfile(version_path) or open(version_path, encoding="utf-8").read().strip() != pin_tag:
        print(f"webmin-pin-mismatch {src}", flush=True)
        raise SystemExit(1)
    print(f"IOC build-image {image}", flush=True)
    work = tempfile.mkdtemp(prefix="webmin-lab-")
    try:
        tar = subprocess.call(
            ["tar", "-C", src, "--exclude", ".git", "-cf", os.path.join(work, "webmin-src.tar"), "."]
        )
        if tar != 0:
            raise SystemExit(tar)
        subprocess.check_call(["cp", dockerfile, os.path.join(work, "Dockerfile")])
        raise SystemExit(subprocess.call(["docker", "build", "-t", image, work]))
    finally:
        subprocess.call(["rm", "-rf", work])
finally:
    fcntl.flock(fd, fcntl.LOCK_UN)
    os.close(fd)
PY
}

trap down EXIT

chmod +x poc.py entrypoint.sh

echo "== py_compile poc.py =="
python3 -m py_compile poc.py

echo "== docker compose down (clean) =="
down

echo "== pin ${PIN_TAG} ${PIN} =="
clone_pin

echo "== flock ${LOCK} image ${IMAGE} =="
if ! ensure_image; then
  fail_setup "image-build-failed"
fi

echo "== docker compose up =="
up_ok=0
for attempt in $(seq 1 8); do
  if docker compose -p "${COMPOSE_PROJECT_NAME}" up -d --no-build; then
    up_ok=1
    break
  fi
  echo "IOC compose-up-retry attempt=${attempt}"
  sleep 8
  down
done
if [[ "${up_ok}" != 1 ]]; then
  fail_setup "compose-up-failed"
fi

echo "== wait ${BASE}/session_login.cgi =="
ready=0
for i in $(seq 1 90); do
  code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 8 \
    -A "h11-lab/2.670" "${BASE}/session_login.cgi" || true)"
  have_user=0
  if docker compose -p "${COMPOSE_PROJECT_NAME}" exec -T webmin \
      grep -q "^limited:" /etc/webmin/miniserv.users 2>/dev/null; then
    have_user=1
  fi
  if [[ "${code}" == "200" && "${have_user}" == 1 ]]; then
    ready=1
    echo "IOC webmin-ready attempt=${i} http=${code} limited=1"
    break
  fi
  echo "IOC webmin-wait attempt=${i} http=${code} limited=${have_user}"
  sleep 2
done
if [[ "${ready}" != 1 ]]; then
  fail_setup "webmin-not-ready"
fi

echo "== poc.py =="
set +e
python3 ./poc.py
rc=$?
set -e

if [[ "${rc}" -ne 0 ]]; then
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 webmin || true
fi

if [[ ! -f poc-last-run.txt ]] || ! tail -n 1 poc-last-run.txt | grep -qE '^(SUCCESS|FAIL) '; then
  echo "FAIL ${LABEL} poc-exit-${rc} ${WITNESS}" >> poc-last-run.txt
  rc=1
fi

exit "${rc}"
