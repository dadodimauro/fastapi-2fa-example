import pytest
from pydantic import ValidationError

from fastapi_2fa_example.auth.schemas import LoginResponse


class TestLoginResponse:
    def test_login_response_2fa_required_valid(self) -> None:
        resp = LoginResponse(requires_2fa=True, tmp_token="tmp", access_token=None)
        assert resp.requires_2fa is True
        assert resp.tmp_token == "tmp"
        assert resp.access_token is None

    def test_login_response_2fa_required_invalid(self) -> None:
        with pytest.raises(ValidationError):
            LoginResponse(requires_2fa=True, tmp_token=None, access_token=None)
        with pytest.raises(ValidationError):
            LoginResponse(
                requires_2fa=True, tmp_token="tmp", access_token="should-not-be-here"
            )

    def test_login_response_no_2fa_valid(self) -> None:
        resp = LoginResponse(requires_2fa=False, tmp_token=None, access_token="access")
        assert resp.requires_2fa is False
        assert resp.access_token == "access"

    def test_login_response_no_2fa_invalid(self) -> None:
        with pytest.raises(ValidationError):
            LoginResponse(requires_2fa=False, tmp_token=None, access_token=None)
