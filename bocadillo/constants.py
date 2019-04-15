import typing

ALL_HTTP_METHODS: typing.Tuple[str, ...] = (
    "GET",
    "HEAD",
    "POST",
    "PUT",
    "DELETE",
    "OPTIONS",
    "PATCH",
)

DEFAULT_CORS_CONFIG = {"allow_origins": [], "allow_methods": ["GET"]}

# See: https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent
WEBSOCKET_CLOSE_CODES: typing.Dict[int, str] = {
    1000: "Normal Closure",
    1001: "Going Away",
    1002: "Protocol Error",
    1003: "Unsupported Type",
    # 1004 is reserved
    1005: "No Status Code [Internal]",
    1006: "Connection Closed Abnormally [Internal]",
    1007: "Invalid Data",
    1008: "Policy Violation",
    1009: "Message Too Big",
    1010: "Extension Required",
    1011: "Internal Error",
    1015: "TLS Failure [Internal]",
}


class CONTENT_TYPE:
    PLAIN_TEXT = "text/plain"
    HTML = "text/html"
    JSON = "application/json"
