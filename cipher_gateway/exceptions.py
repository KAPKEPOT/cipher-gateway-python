# cipher_gateway/exceptions.py
"""
CipherGateway SDK exception hierarchy.
All exceptions inherit from CipherGatewayError for easy catch-all handling.

    try:
        await client.wait_for_active(account_id)
    except AccountLoginFailedError as e:
        print(f"Wrong credentials: {e}")
    except CipherGatewayError as e:
        print(f"Gateway error: {e}")
"""


class CipherGatewayError(Exception):
    """Base exception for all SDK errors. Catch this for a catch-all."""
    pass


class NotStartedError(CipherGatewayError):
    """Client was used before start() was called (or outside async with block)."""
    pass


class AuthenticationError(CipherGatewayError):
    """API key is missing, invalid, or has been revoked."""
    pass


class AccountNotFoundError(CipherGatewayError):
    """The given account_id does not exist on the gateway."""
    pass


class AccountLoginFailedError(CipherGatewayError):
    """MT5 credentials were rejected by the broker."""
    pass


class AccountTimeoutError(CipherGatewayError):
    """Account did not reach 'active' status within the timeout."""
    pass


class OrderError(CipherGatewayError):
    """Order placement, modification, or close failed."""
    pass


class GatewayConnectionError(CipherGatewayError):
    """
    HTTP or WebSocket connection to the gateway failed.

    Named GatewayConnectionError (not ConnectionError) to avoid shadowing
    Python's built-in builtins.ConnectionError, which is a subclass of OSError
    and used by socket/network code throughout the stdlib.
    """
    pass


class SubscriptionError(CipherGatewayError):
    """WebSocket market-data subscription failed or timed out."""
    pass


class GatewayResponseError(CipherGatewayError):
    """
    Gateway returned an unexpected or malformed HTTP response.

    Attributes:
        status_code: The HTTP status code (e.g. 500).
        raw:         The raw response body (truncated for HTML error pages).
    """
    def __init__(self, message: str, status_code: int = 0, raw: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.raw = raw
