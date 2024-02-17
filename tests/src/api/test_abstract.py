import sys

sys.path.append("hamiltoniansports")
# appending the application dir to sys ensures tests run using the correct relative imports
# and also keep tests out of docker container / application code

import pytest
import json
from pathlib import Path
from datetime import datetime
import shutil
from unittest.mock import Mock, patch, mock_open
from hamiltoniansports.src.api.abstract import APIAbstract
from hamiltoniansports.src.api.models import SeasonResults, GameResult, Team


class DummyResults:
    """helper class to create dummy model data for algo / api testing.
    Note that pydantic model structre/behaviour tests are done in dedicate tests elsewhere
    """

    def __init__(self):
        self.cur_dt = datetime.now()
        self.team1 = Team(
            id=1,
            name="Team1",
            logo_url="http://example.com/logo1.png",
            logo_file=Path("/path/to/logo1.png"),
        )
        self.team2 = Team(
            id=2,
            name="Team2",
            logo_url="http://example.com/logo2.png",
            logo_file=Path("/path/to/logo2.png"),
        )
        self.team3 = Team(
            id=3,
            name="Team3",
            logo_url="http://example.com/logo3.png",
            logo_file=Path("/path/to/logo3.png"),
        )
        self.game_result1 = GameResult(
            winner=1, loser=2, round=1, winner_score=3, loser_score=2, dt=self.cur_dt
        )
        self.game_result2 = GameResult(
            winner=1,
            loser=3,
            round=2,
            winner_score=3,
            loser_score=2,
            dt=datetime(year=2022, month=5, day=2),
        )
        self.game_result3 = GameResult(
            winner=2,
            loser=3,
            round=2,
            winner_score=3,
            loser_score=2,
            dt=datetime(year=2022, month=7, day=3),
        )
        self.game_result4 = GameResult(
            winner=3,
            loser=1,
            round=3,
            winner_score=3,
            loser_score=2,
            dt=datetime(year=2022, month=11, day=11),
        )
        round_results = {
            1: [self.game_result1],
            2: [self.game_result2, self.game_result3],
            3: [self.game_result4],
        }
        teams = {1: self.team1, 2: self.team2, 3: self.team3}
        self.season_results = SeasonResults(
            league="TestLeague", season="2022", round_results=round_results, teams=teams
        )


class DummyAPI(APIAbstract):
    """helper class for API interaction"""

    def __init__(
        self,
        league: str,
        season: str | int,
        api_url: str,
        resource_url: str,
        seasonresults: SeasonResults,
    ):
        self.league = league
        self.season = season
        self.api_url = api_url
        self.resource_url = resource_url
        self.seasonresults = seasonresults

    def _validate_season_for_api(self, season_value: str) -> None:
        # dummy implementation of abstract method
        pass

    def _set_headers(self) -> None:
        # dummy implementation of abstract method
        pass

    def get_season_results(self):
        # dummy implementation of abstract method
        pass

    def get_team_resources(self):
        # dummy implementation of abstract method
        pass


def test_api_abstract():
    """test basics of the abstract class, using a dummy DummyAPI concrete class"""
    dummy: DummyResults = DummyResults()

    valid_data: dict[str, str | SeasonResults] = {
        "league": "TestLeague",
        "season": "2022",
        "api_url": "https://api.example.com",
        "resource_url": "https://resource.example.com",
        "seasonresults": dummy.season_results,
    }

    test_api: DummyAPI = DummyAPI(**valid_data)

    # positive checks
    # type checking
    assert isinstance(test_api.league, str)
    assert isinstance(test_api.season, (str, int))
    assert isinstance(test_api.api_url, str)
    assert isinstance(test_api.resource_url, str)
    assert isinstance(test_api.seasonresults, SeasonResults)

    # value checking
    assert test_api.league == "TestLeague"
    assert test_api.season == "2022"
    assert test_api.api_url == "https://api.example.com"
    assert test_api.resource_url == "https://resource.example.com"
    assert test_api.seasonresults == dummy.season_results

    # dynamic value checking
    assert test_api.output_path == Path(f"./data/{test_api.league}/{test_api.season}")
    assert (
        test_api.season_results_cached_file
        == test_api.output_path / "season_results_cache.json"
    )
    assert (
        test_api.team_resources_cached_file
        == test_api.output_path / "team_resources_cache.json"
    )

    # negative tests
    # ensure TypeError if any req attributes are missing
    for key in valid_data.keys():
        invalid_data = valid_data.copy()
        del invalid_data[key]
        with pytest.raises(TypeError):
            DummyAPI(**invalid_data)


def test_api_response_helper_success():
    """test staticmethod api_response_helper withing mocking, assert the response"""
    with patch("requests.get") as mock_get:
        mock_response: Mock = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "json"}
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        url = "https://api.example.com"
        headers = {"header": "value"}
        data = DummyAPI.api_response_helper(url, headers)

        mock_get.assert_called_once_with(url, headers=headers)

        mock_response.json.assert_called_once()

        assert data == {"key": "value"}


def test_api_response_helper_failure_status_code():
    """test staticmethod api_response_helper fails for numerous 4-- and 5-- status codes with mocking"""
    status_codes = [400, 401, 404, 500, 513, 599]

    for status_code in status_codes:
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_get.return_value = mock_response

            url = "https://api.example.com"
            headers = {"header": "value"}
            with pytest.raises(ValueError):
                DummyAPI.api_response_helper(url, headers)


def test_api_response_helper_failure_content_type():
    """test staticmethod api_response_helper fails for not-implemented response types with mocking"""
    content_types = ["csv", "xml", "ogg", "css", "html"]

    for content_type in content_types:
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"Content-Type": content_type}
            mock_get.return_value = mock_response

            url = "https://api.example.com"
            headers = {"header": "value"}
            with pytest.raises(ValueError):
                DummyAPI.api_response_helper(url, headers)


def test_download_helper():
    """test staticmethod download_helper succeeds using mocking"""
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"test2000wowee"
        mock_get.return_value = mock_response

        with patch("builtins.open", mock_open()) as mock_file:
            with patch.object(Path, "exists", return_value=False), patch.object(
                Path, "mkdir"
            ):
                url = "https://file.example.com"
                store_filepath = Path("file.txt")
                DummyAPI.download_helper(url, store_filepath)

                # assertions
                mock_get.assert_called_once_with(url)
                mock_file().write.assert_called_once_with(mock_response.content)


def test_cache_api_response_success():
    """test staticmethod cache_api_response success using mocking"""
    with patch("json.dump") as mock_dump:
        with patch("builtins.open", mock_open()) as mock_file:
            with patch.object(Path, "exists", return_value=False), patch.object(
                Path, "mkdir"
            ):
                data = {"key": "value"}
                data_type = "json"
                path = Path("file.json")
                DummyAPI.cache_api_response(data, data_type, path)

                mock_file.assert_called_once_with(path, "w")
                mock_dump.assert_called_once_with(data, mock_file(), indent=2)


def test_cache_api_response_failure_data_type():
    """test staticmethod cache_api_response failure based on content_type"""
    data = {"key": "value"}
    data_type = "invalid"
    path = Path("file.json")
    with pytest.raises(ValueError):
        DummyAPI.cache_api_response(data, data_type, path)


def test_load_cached_api_data_helper_success():
    """test staticmethod load_cached_api_data_helper using mocking"""
    with patch("builtins.open", mock_open(read_data='{"key": "value"}')) as mock_file:
        with patch.object(Path, "exists", return_value=True):
            path = Path("file.json")
            data = DummyAPI.load_cached_api_data_helper(path, "json")

            mock_file.assert_called_once_with(path, "r")
            assert data == {"key": "value"}


def test_load_cached_api_data_helper_failure_file_type():
    """test staticmethod load_cached_api_data_helper failure based on file_type argument"""
    path = Path("file.json")
    with pytest.raises(ValueError):
        DummyAPI.load_cached_api_data_helper(path, file_type="invalid_file_type_value")


def test_load_cached_api_data_helper_failure_file_not_found():
    """test staticmethod load_cached_api_data_helper failure for no file found using mocking"""
    with patch.object(Path, "exists", return_value=False):
        path = Path("file.json")
        with pytest.raises(FileNotFoundError):
            DummyAPI.load_cached_api_data_helper(path, file_type="json")


def test_clear_cache():
    """test clear_cache method using mocking.
    As this one isn't a staticmethod, am required to instanciate a class object
    """
    with patch("shutil.rmtree") as mock_rmtree:
        dummy: DummyResults = DummyResults()

        valid_data: dict[str, str | SeasonResults] = {
            "league": "TestLeague",
            "season": "2022",
            "api_url": "https://api.example.com",
            "resource_url": "https://resource.example.com",
            "seasonresults": dummy.season_results,
        }

        test_api: DummyAPI = DummyAPI(**valid_data)

        test_api.clear_cache()

        mock_rmtree.assert_called_once_with(test_api.output_path)


def test_clear_cache_file_not_found():
    """Test clear_cache method handles FileNotFoundError."""
    with patch("shutil.rmtree", side_effect=FileNotFoundError) as mock_rmtree:
        dummy: DummyResults = DummyResults()

        valid_data: dict[str, str | SeasonResults] = {
            "league": "TestLeague",
            "season": "2022",
            "api_url": "https://api.example.com",
            "resource_url": "https://resource.example.com",
            "seasonresults": dummy.season_results,
        }

        test_api: DummyAPI = DummyAPI(**valid_data)

        try:
            test_api.clear_cache()
        except FileNotFoundError:
            pytest.fail("FileNotFoundError was not handled")

        mock_rmtree.assert_called_once_with(test_api.output_path)
