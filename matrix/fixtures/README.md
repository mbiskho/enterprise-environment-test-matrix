Put the test corporate CA here as `corp-ca.pem` (a throwaway CA generated for CI, never a real customer CA).
The `bank-locked-down` and `tls-intercepting-proxy` environments point CA_BUNDLE at it.
