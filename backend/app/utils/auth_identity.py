from typing import Any

import google.auth


def get_auth_principal(credentials: Any = None) -> str:
    """Return the non-secret identity represented by ADC credentials."""
    try:
        if credentials is None:
            credentials, _ = google.auth.default()

        service_account_email = getattr(credentials, "service_account_email", None)
        if service_account_email:
            return service_account_email

        target_principal = getattr(credentials, "_target_principal", None)
        if target_principal:
            return target_principal

        account = getattr(credentials, "_account", None)
        if account:
            return account
    except Exception:
        pass

    return "unknown ADC principal"