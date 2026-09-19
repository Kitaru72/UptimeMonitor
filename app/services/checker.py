from time import perf_counter

import httpx


async def check_url(url: str) -> dict:
    started_at = perf_counter()

    async with httpx.AsyncClient(
        timeout=5.0,
        follow_redirects=False,
    ) as client:
        try:
            response = await client.get(url)

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
            error_type = "CONNECTION_ERROR"
            http_status_code = None

        except httpx.RequestError:
            status = "DOWN"
            error_type = "REQUEST_ERROR"
            http_status_code = None

    duration_ms = round((perf_counter() - started_at) * 1000)

    return {
        "status": status,
        "http_status_code": http_status_code,
        "error_type": error_type,
        "duration_ms": duration_ms,
    }
