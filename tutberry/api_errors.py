"""Consistent problem responses for DRF validation and permission errors."""
from rest_framework.views import exception_handler


def problem(status_code, title, detail, *, errors=None):
    body = {
        "type": "about:blank",
        "title": title,
        "status": status_code,
        "detail": str(detail),
    }
    if errors is not None:
        body["errors"] = errors
    return body


_TITLES = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    409: "Conflict",
    429: "Too Many Requests",
}


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None
    data = response.data
    detail = data.get("detail") if isinstance(data, dict) else None
    if detail is None:
        detail = "Request validation failed"
    response.data = problem(
        response.status_code,
        _TITLES.get(response.status_code, "Request Error"),
        detail,
        errors=data if detail == "Request validation failed" else None,
    )
    response["Content-Type"] = "application/problem+json"
    return response
