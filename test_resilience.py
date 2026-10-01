import pytest
from unittest.mock import AsyncMock, patch
from main import get_data_protected

@pytest.mark.asyncio
async def test_resilience_fallback_and_retry():
    mock_fetch = AsyncMock(side_effect=Exception("External Service Timeout"))

    with patch("main.fetch_external_data_with_retry", mock_fetch):
        result = await get_data_protected()

        assert result["status"] == "degraded"
        assert result["is_fallback"] is True
        assert result["data"] == "Cached Default Data (Fallback)"

        assert mock_fetch.call_count == 1