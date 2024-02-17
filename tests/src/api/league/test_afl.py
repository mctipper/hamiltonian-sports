import sys

sys.path.append("hamiltoniansports")
# appending the application dir to sys ensures tests run using the correct relative imports
# and also keep tests out of docker container / application code

import pytest
from datetime import datetime
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from hamiltoniansports.src.api.models import SeasonResults, GameResult, Team
from hamiltoniansports.utils.config import Config
from hamiltoniansports.src.api.leagues.afl import AFLsquiggleAPI
from hamiltoniansports.src.api.leagues.afl import Config as AFLsquiggleAPIConfig


def test_config_for_afl():
    """more of a test for Config than AFLsquiggleAPI, ensures that Config is setup as expected"""
    assert "afl" in Config.valid_leagues_seasons
    assert isinstance(Config.valid_leagues_seasons["afl"], list)
    assert Config.valid_leagues_seasons["afl"][0] == "1897"
    assert Config.valid_leagues_seasons["afl"][-1] == "2999"


def test_init():
    """test of __init__ attribute assignment and calling of correct private methods"""
    with patch.object(
        AFLsquiggleAPI, "_validate_season_for_api"
    ) as mock_validate_season:
        with patch.object(AFLsquiggleAPI, "_set_headers") as mock_set_headers:
            afl_api = AFLsquiggleAPI(league="afl", season_str="2023")

            assert afl_api.league == "afl"
            assert afl_api.api_url == "https://api.squiggle.com.au/"
            assert afl_api.resource_url == "https://squiggle.com.au"

            mock_validate_season.assert_called_once_with("2023")
            mock_set_headers.assert_called_once()


def test_validate_season_for_api():
    """test of private method _validate_season_for_api"""
    afl_api = AFLsquiggleAPI(league="afl", season_str="2023")

    # ensure the string version of season is convert to an integer correctly
    assert isinstance(afl_api.season, int)
    assert afl_api.season == 2023

    # invalid seasons passed
    with pytest.raises(ValueError):
        afl_api._validate_season_for_api("1890")

    with pytest.raises(ValueError):
        afl_api._validate_season_for_api("3000")


def test_set_headers():
    """testing private method _set_headers to ensure is called and updates the
    .headers dict correctly
    """
    afl_api = AFLsquiggleAPI(league="afl", season_str="2023")

    with patch.object(AFLsquiggleAPIConfig, "email", new="test@test.com"):
        afl_api._set_headers()
        assert afl_api.headers == {"User-Agent": "test@test.com"}

    with patch("logging.Logger.warning") as mock_warning:
        with patch.object(AFLsquiggleAPIConfig, "email", new="dummy@email.com"):
            afl_api._set_headers()
            assert afl_api.headers == {"User-Agent": "dummy@email.com"}
            mock_warning.assert_called_once_with(
                "Please update your email address in ./utils/config.py"
            )

    # error out if empty string
    with patch.object(AFLsquiggleAPIConfig, "email", new=""), pytest.raises(ValueError):
        afl_api._set_headers()

    # error out if None
    with patch.object(AFLsquiggleAPIConfig, "email", new=None), pytest.raises(
        ValueError
    ):
        afl_api._set_headers()


class TestDataProcessing(unittest.TestCase):
    """class of similar tests, ensuring that API results (whether stored in the cache or not) are
    processed and stored correctly.

    Sample data is used for testing. Note that testing of the pydantic models is handled in their
    own dedicated tests
    """

    season_result_data = {
        "games": [
            {
                "round": 1,
                "hscore": 100,
                "ascore": 80,
                "winnerteamid": 1,
                "hteamid": 1,
                "ateamid": 2,
                "date": "2023-03-24 19:50:00",
            },
            {
                "round": 1,
                "hscore": 81,
                "ascore": 101,
                "winnerteamid": 3,
                "hteamid": 4,
                "ateamid": 3,
                "date": "2023-03-25 19:50:00",
            },
            {
                "round": 2,
                "hscore": 105,
                "ascore": 85,
                "winnerteamid": 1,
                "hteamid": 1,
                "ateamid": 3,
                "date": "2023-04-24 20:50:00",
            },
        ]
    }

    expected_result_no_teams = SeasonResults(
        league="afl",
        season="2023",
        round_results={
            1: [
                GameResult(
                    winner=1,
                    loser=2,
                    round=1,
                    winner_score=100,
                    loser_score=80,
                    dt=datetime.strptime("2023-03-24 19:50:00", "%Y-%m-%d %H:%M:%S"),
                ),
                GameResult(
                    winner=3,
                    loser=4,
                    round=1,
                    winner_score=101,
                    loser_score=81,
                    dt=datetime.strptime("2023-03-25 19:50:00", "%Y-%m-%d %H:%M:%S"),
                ),
            ],
            2: [
                GameResult(
                    winner=1,
                    loser=3,
                    round=2,
                    winner_score=105,
                    loser_score=85,
                    dt=datetime.strptime("2023-04-24 20:50:00", "%Y-%m-%d %H:%M:%S"),
                ),
            ],
        },
        teams={},
    )

    team_data = {
        "teams": [
            {"id": 1, "name": "Team 1", "logo": "/logos/team1.png"},
            {"id": 2, "name": "Team 2", "logo": "/logos/team2.png"},
            {"id": 3, "name": "Team 3", "logo": "/logos/team3.png"},
            {"id": 4, "name": "Team 4", "logo": "/logos/team4.png"},
            {"id": 5, "name": "Team 5", "logo": "/logos/team5.png"},
        ]
    }

    expected_result_with_teams = SeasonResults(
        league="afl",
        season="2023",
        round_results={
            1: [
                GameResult(
                    winner=1,
                    loser=2,
                    round=1,
                    winner_score=100,
                    loser_score=80,
                    dt=datetime.strptime("2023-03-24 19:50:00", "%Y-%m-%d %H:%M:%S"),
                ),
                GameResult(
                    winner=3,
                    loser=4,
                    round=1,
                    winner_score=101,
                    loser_score=81,
                    dt=datetime.strptime("2023-03-25 19:50:00", "%Y-%m-%d %H:%M:%S"),
                ),
            ],
            2: [
                GameResult(
                    winner=1,
                    loser=3,
                    round=2,
                    winner_score=105,
                    loser_score=85,
                    dt=datetime.strptime("2023-04-24 20:50:00", "%Y-%m-%d %H:%M:%S"),
                ),
            ],
        },
        teams={
            1: Team(
                id=1,
                name="Team 1",
                logo_url="https://squiggle.com.au/logos/team1.png",
                logo_file=Path("data/afl/2023/logos/Team 1.png"),
            ),
            2: Team(
                id=2,
                name="Team 2",
                logo_url="https://squiggle.com.au/logos/team2.png",
                logo_file=Path("data/afl/2023/logos/Team 2.png"),
            ),
            3: Team(
                id=3,
                name="Team 3",
                logo_url="https://squiggle.com.au/logos/team3.png",
                logo_file=Path("data/afl/2023/logos/Team 3.png"),
            ),
            4: Team(
                id=4,
                name="Team 4",
                logo_url="https://squiggle.com.au/logos/team4.png",
                logo_file=Path("data/afl/2023/logos/Team 4.png"),
            ),
        },
    )

    def test_get_season_results(self):
        """test that get_season_results method correct parses the data, from API or local cache"""
        # test 'api_resonse_helper', ie. data returned from api, not local cache
        afl_api = AFLsquiggleAPI(league="afl", season_str="2023")

        with patch.object(afl_api, "load_cached_api_data_helper"), patch.object(
            afl_api, "api_response_helper", return_value=self.season_result_data
        ), patch.object(afl_api, "cache_api_response"), patch.object(
            type(afl_api.season_results_cached_file), "exists", new_callable=MagicMock
        ) as season_results_cached:
            season_results_cached.return_value = False
            afl_api.get_season_results()

            assert afl_api.seasonresults == self.expected_result_no_teams

        # test 'load_cached_api_data_helper', ie. data returned from local cache, not API
        afl_api = AFLsquiggleAPI(league="afl", season_str="2023")

        with patch.object(
            afl_api, "load_cached_api_data_helper", return_value=self.season_result_data
        ), patch.object(afl_api, "api_response_helper"), patch.object(
            afl_api, "cache_api_response"
        ), patch.object(
            type(afl_api.season_results_cached_file), "exists", new_callable=MagicMock
        ) as season_results_cached:
            season_results_cached.return_value = True
            afl_api.get_season_results()

            assert afl_api.seasonresults == self.expected_result_no_teams

    def test_get_team_resources(self):
        """test that get_team_resources method correct parses the data, from API or local cache.
        Checks if teams that did not play that season are removed, and that appropriate errors
        are raised if get_ methods are called out-of-expected-order
        """
        # test 'load_cached_api_data_helper', ie. data returned from local cache, not API
        afl_api = AFLsquiggleAPI(league="afl", season_str="2023")

        with patch.object(
            afl_api, "load_cached_api_data_helper", return_value=self.season_result_data
        ), patch.object(afl_api, "cache_api_response"), patch.object(
            type(afl_api.season_results_cached_file), "exists", return_value=True
        ) as season_results_cached:
            afl_api.get_season_results()

        with patch.object(
            afl_api, "api_response_helper", return_value=self.team_data
        ), patch.object(afl_api, "cache_api_response"), patch.object(
            afl_api, "download_helper"
        ), patch.object(
            type(afl_api.team_resources_cached_file), "exists", return_value=False
        ) as team_resources_cached:
            afl_api.get_team_resources()

        # expected results
        assert afl_api.seasonresults == self.expected_result_with_teams
        # 'Team 5' included in input but removed from output since there are no results containing this team
        assert self.team_data["teams"][4]["id"] == 5
        assert "5" not in afl_api.seasonresults.teams

        # test 'api_resonse_helper', ie. data returned from api, not local cache
        afl_api = AFLsquiggleAPI(league="afl", season_str="2023")

        with patch.object(
            afl_api, "load_cached_api_data_helper", return_value=self.season_result_data
        ), patch.object(afl_api, "cache_api_response"), patch.object(
            type(afl_api.season_results_cached_file), "exists", return_value=True
        ) as season_results_cached:
            afl_api.get_season_results()

        with patch.object(
            afl_api, "load_cached_api_data_helper", return_value=self.team_data
        ), patch.object(afl_api, "cache_api_response"), patch.object(
            afl_api, "download_helper"
        ), patch.object(
            type(afl_api.team_resources_cached_file), "exists", return_value=True
        ) as team_resources_cached:
            afl_api.get_team_resources()

        # expected results
        assert afl_api.seasonresults == self.expected_result_with_teams
        # 'Team 5' included in input but removed from output since there are no results containing this team
        assert self.team_data["teams"][4]["id"] == 5
        assert "5" not in afl_api.seasonresults.teams

        # test that .get_team_resources() cannot be called before .get_season_results()
        afl_api = AFLsquiggleAPI(league="afl", season_str="2023")

        with patch.object(
            afl_api, "load_cached_api_data_helper", return_value=self.season_result_data
        ), patch.object(afl_api, "cache_api_response"), patch.object(
            type(afl_api.season_results_cached_file), "exists", return_value=True
        ) as season_results_cached:
            with pytest.raises(RuntimeError):
                afl_api.get_team_resources()
