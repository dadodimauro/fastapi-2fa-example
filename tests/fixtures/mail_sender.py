from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def mock_send_email() -> Generator[AsyncMock]:
    with patch(
        "fastapi_2fa_example.auth.router.send_email", new_callable=AsyncMock
    ) as mock:
        yield mock
        mock.reset_mock()
