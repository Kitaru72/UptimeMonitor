import httpx
import pytest
import respx

from app.services.batch_checker import check_urls


@pytest.mark.anyio
@respx.mock
async def test_check_urls_returns_results_in_input_order():
    urls = [
        "https://example.com",
        "https://example2.com",
    ]
    respx.get(urls[0]).mock(
        return_value=httpx.Response(200)
    )
    respx.get(urls[1]).mock(
        return_value=httpx.Response(500)
    )

    results = await check_urls(urls)

    assert len(results) == 2

    assert results[0]["status"] == "UP"
    assert results[0]["http_status_code"] == 200

    assert results[1]["status"] == "DOWN"
    assert results[1]["http_status_code"] == 500
