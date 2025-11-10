import pytest
from unittest.mock import MagicMock
from modules.informatics_api import InformaticsAPI


@pytest.fixture
def api():
    return InformaticsAPI(session=MagicMock())


def test_extract_id_from_href(api):
    assert api._extract_id_from_href("https://informatics.msk.ru/mod/statements/view.php?id=94601") == "94601"
    assert api._extract_id_from_href(None) is None


def test_login_handles_invalid_response(api):
    api.session.get.return_value.status_code = 404
    assert not api.login("user", "pass")
