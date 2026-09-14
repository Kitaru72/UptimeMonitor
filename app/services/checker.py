from time import perf_counter

import httpx


def check_url(url: str) -> dict:
    started_at = perf_counter()

    try:
        response = httpx.get(url, timeout=5.0, follow_redirects=False)

        http_status_code = response.status_code
        error_type = None
        if 200 <= http_status_code < 400:
            status = "UP"
        else:
            status = "DOWN"

    except httpx.TimeoutException:
        status = "DOWN"
        error_type = "TIMEOUT"
        http_status_code = None

    except httpx.ConnectError:
        status = "DOWN"
        error_type = "DNS_ERROR"
        http_status_code = None

    duration_ms = round((perf_counter() - started_at) * 1000)

    return {
        "status": status,
        "http_status_code": http_status_code,
        "error_type": error_type,
        "duration_ms": duration_ms,
    }