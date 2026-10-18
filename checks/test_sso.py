import datetime as dt
import email.utils
import re

import httpx

from conftest import need


def fetch_metadata() -> httpx.Response:
    r = httpx.get(need("SSO_METADATA_URL"), timeout=10)
    r.raise_for_status()
    return r


def test_idp_metadata_is_saml():
    body = fetch_metadata().text
    assert "EntityDescriptor" in body and "X509Certificate" in body, "metadata isn't SAML or has no signing cert"


def test_clock_skew_under_two_minutes():
    # SAML assertions are rejected when clocks disagree by more than a few minutes.
    r = fetch_metadata()
    server = email.utils.parsedate_to_datetime(r.headers["date"])
    skew = abs((dt.datetime.now(dt.timezone.utc) - server).total_seconds())
    assert skew < 120, f"clock skew {skew:.0f}s with the IdP; fix NTP before enabling SSO"


def test_signing_certificate_present_once_or_more():
    certs = re.findall(r"<(?:ds:)?X509Certificate>([^<]+)<", fetch_metadata().text)
    assert certs, "no signing certificate in metadata"
