import os

import httpx
import pytest

from conftest import need

OUTBOUND = ["https://api.openai.com", "https://pypi.org/simple/"]


def client(**kw) -> httpx.Client:
    return httpx.Client(timeout=10, verify=os.environ.get("CA_BUNDLE", True), **kw)


@pytest.mark.parametrize("url", OUTBOUND)
def test_outbound_https_through_proxy(url):
    proxy = need("HTTPS_PROXY")
    with client(proxy=proxy) as c:
        r = c.get(url)
    assert r.status_code < 500, f"{url} via {proxy}: HTTP {r.status_code}"


def test_internal_hosts_bypass_proxy():
    need("HTTPS_PROXY")
    no_proxy = os.environ.get("NO_PROXY", "")
    for host in ("localhost", "127.0.0.1"):
        assert host in no_proxy, f"{host} must be in NO_PROXY or local calls go through the proxy"
