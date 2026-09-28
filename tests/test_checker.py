import httpx
import pytest
import respx

from app.services.checker import check_url


@pytest.mark.anyio
@respx.mock
async def test_check_url_returns_up_for_successful_response():
    url = "https://example.com"
    respx.get(url).mock(
        return_value=httpx.Response(200)
    )

    result = await check_url(url)

    assert result["status"] == "UP"
    assert result["http_status_code"] == 200
    assert result["error_type"] is None


@pytest.mark.anyio
@respx.mock
async def test_check_url_returns_timeout_when_request_times_out():
    url = "https://example.com"
    respx.get(url).mock(
        side_effect=httpx.TimeoutException("Request timed out")
    )

    result = await check_url(url)

    assert result["status"] == "DOWN"
    assert result["http_status_code"] is None
    assert result["error_type"] == "TIMEOUT"


@pytest.mark.anyio
@respx.mock
async def test_check_url_returns_connection_error_when_connection_fails():
    url = "https://example.com"
    respx.get(url).mock(
        side_effect=httpx.ConnectError("Connection failed")
    )

    result = await check_url(url)

    assert result["status"] == "DOWN"
    assert result["http_status_code"] is None
    assert result["error_type"] == "CONNECTION_ERROR"
