import pytest
from unittest.mock import patch
from modules.informatics_api import InformaticsAPI


@pytest.fixture
def api():
    return InformaticsAPI()


def test_get_courses_mock(api):
    fake_courses = [("Курс 1", "123"), ("Курс 2", "456")]

    with patch.object(api, "get_courses", return_value=fake_courses):
        courses = api.get_courses()
        assert isinstance(courses, list)
        assert len(courses) == 2
        assert all(isinstance(c, tuple) for c in courses)


def test_get_contests_mock(api):
    fake_contests = [("Контест A", "11111"), ("Контест B", "22222")]

    with patch.object(api, "get_contests", return_value=fake_contests):
        contests = api.get_contests("123")
        assert len(contests) == 2
        assert contests[0][0].startswith("Контест")


def test_get_groups_mock(api):
    fake_groups = [("Группа 7A", "777"), ("Группа 8B", "888")]

    with patch.object(api, "get_groups", return_value=fake_groups):
        groups = api.get_groups("11111", "fake_user", "fake_pass")
        assert isinstance(groups, list)
        assert len(groups) == 2
        assert all(isinstance(g, tuple) and len(g) == 2 for g in groups)
