# Enterprise Environment Test Matrix

"Does it work on our setup?" is the first question every enterprise customer asks. This repo answers it with a test matrix of the environments customers actually run (database versions, proxies, custom certificate authorities, SSO providers) and one compatibility table generated from the results.

```
environments.yaml ──► generate.py ──► .github/workflows/matrix.yml (one CI job per environment)
                                              │  each job: start the environment, run checks/
                                              ▼
                                    junit XML per environment ──► report.py ──► COMPATIBILITY.md
```

## What's tested

`checks/` is a pytest suite that runs *against* an environment through environment variables, so the same checks run in CI and on a customer's jump box:

| Check | Catches |
|---|---|
| `test_database.py` | unsupported Postgres version, missing extension, SSL mode the customer enforces |
| `test_network.py` | outbound blocked without the proxy, proxy that breaks TLS, `NO_PROXY` gaps for internal hosts |
| `test_tls.py` | services signed by a corporate CA we don't trust yet |
| `test_sso.py` | IdP metadata unreachable, signing certificate expiring, clock skew that breaks SAML |

Run on a customer machine:

```bash
pip install -r checks/requirements.txt
DATABASE_URL=postgres://... HTTPS_PROXY=http://proxy:3128 SSO_METADATA_URL=https://idp/metadata \
CA_BUNDLE=/etc/pki/corp-ca.pem pytest checks -v --junitxml=result.xml
```

## Adding an environment

Add an entry to `matrix/environments.yaml` and run `python matrix/generate.py`. The workflow file is generated, never hand-edited, so the matrix and CI can't drift apart.

## Layout

```
matrix/environments.yaml    the supported matrix (what we promise customers)
matrix/generate.py          environments.yaml → GitHub Actions workflow
matrix/report.py            junit results → COMPATIBILITY.md
checks/                     environment checks (pytest), configured by env vars
```
