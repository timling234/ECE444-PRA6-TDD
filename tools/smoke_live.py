"""Exercise the real deployed HTTP service using disposable demo posts."""

import argparse
from datetime import datetime, timezone
from http.cookiejar import CookieJar
import json
import re
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import build_opener, HTTPCookieProcessor


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    client = build_opener(HTTPCookieProcessor(CookieJar()))
    anonymous = build_opener(HTTPCookieProcessor(CookieJar()))

    def request(opener, path, data=None):
        body = urlencode(data).encode() if data is not None else None
        try:
            with opener.open(base + path, data=body, timeout=90) as response:
                return response.status, response.read().decode()
        except HTTPError as error:
            return error.code, error.read().decode()

    status, body = request(client, "/")
    assert status == 200 and "<h1>Flaskr</h1>" in body, (status, body[:120])
    print("PASS public home page", flush=True)
    status, body = request(client, "/login", {"username": "admin", "password": "admin"})
    assert status == 200 and "You were logged in" in body
    print("PASS login and redirect", flush=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    title = f"PRA6 smoke {stamp}"
    status, body = request(
        client,
        "/add",
        {"title": title, "text": "UniqueNeedle <strong>remote persistence</strong>"},
    )
    assert status == 200 and title in body
    match = re.search(r'<h2 id="(\d+)">' + re.escape(title) + r"</h2>", body)
    assert match, body[:120]
    post_id = match.group(1)
    print("PASS authenticated post creation; id=" + post_id, flush=True)
    status, body = request(anonymous, "/")
    assert status == 200 and title in body
    print("PASS fresh session reads persisted post", flush=True)
    status, body = request(client, "/search/?query=uniqueneedle")
    assert status == 200 and title in body
    print("PASS case-insensitive body search", flush=True)
    status, body = request(anonymous, "/delete/" + post_id)
    assert status == 401 and json.loads(body)["status"] == 0
    assert title in request(anonymous, "/")[1]
    print("PASS anonymous deletion denied; row preserved", flush=True)
    status, body = request(client, "/delete/" + post_id)
    assert status == 200 and json.loads(body)["status"] == 1
    assert title not in request(anonymous, "/")[1]
    print("PASS authenticated deletion; fresh-session absence", flush=True)
    status, body = request(client, "/logout")
    assert status == 200 and "You were logged out" in body
    print("PASS logout", flush=True)
    print("All real HTTP smoke checks passed. Disposable post removed.", flush=True)


if __name__ == "__main__":
    main()
