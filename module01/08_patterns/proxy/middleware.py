"""A protection proxy for the statusboard app (see app.py's bottom section).

`03_proxy_middleware.py` builds the same idea on a toy `Request`/`Response`.
WSGI is that idea running for real: this middleware has the exact same
interface as the app it wraps — `(environ, start_response) -> iterable[bytes]`
— and can answer without ever calling through to it. That shared interface is
the whole definition of a Proxy; Flask, Django and every ASGI framework build
their middleware stacks on exactly this shape.

Same idea as `BlockIPMiddleware` in `../../patterns/middleware.py`, written
as a plain function instead of an `__init__`/`__call__` class. Django's
middleware protocol asks for an object with that shape; WSGI only asks for a
callable, so a closure does the same job with one less concept.
"""

_BLOCKED_IPS = {"192.168.1.10", "10.0.0.1"}  # add blocked addresses here


def _client_ip(environ):
    """Same lookup as Django's `get_client_ip`: prefer the forwarded header,
    fall back to the socket address. A reverse proxy overwrites `REMOTE_ADDR`
    with its own address, so without this a deployment behind one would see
    every visitor as the same IP.
    """
    forwarded_for = environ.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return environ.get("REMOTE_ADDR")


def block_ip_middleware(app):
    """A protection proxy: a blocked address never reaches Flask at all."""

    def wrapped(environ, start_response):
        print(_client_ip(environ))
        if _client_ip(environ) in _BLOCKED_IPS:
            body = b"forbidden\n"
            start_response(
                "403 Forbidden",
                [("Content-Type", "text/plain"), ("Content-Length", str(len(body)))],
            )
            return [body]
        return app(environ, start_response)

    return wrapped
