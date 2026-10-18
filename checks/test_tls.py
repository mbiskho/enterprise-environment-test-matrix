import os
import ssl

import httpx
import pytest

from conftest import need


def test_corporate_ca_bundle_is_valid_pem():
    path = need("CA_BUNDLE")
    ctx = ssl.create_default_context()
    ctx.load_verify_locations(cafile=path)  # raises if the file isn't usable
    assert ctx.cert_store_stats()["x509_ca"] >= 1


def test_tls_intercepting_proxy_is_trusted():
    proxy = need("HTTPS_PROXY")
    ca = os.environ.get("CA_BUNDLE")
    try:
        with httpx.Client(proxy=proxy, verify=ca or True, timeout=10) as c:
            c.get("https://pypi.org/simple/")
    except httpx.ConnectError as e:
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
            pytest.fail("proxy re-signs HTTPS with a CA we don't trust: set CA_BUNDLE to the corporate CA")
        raise
