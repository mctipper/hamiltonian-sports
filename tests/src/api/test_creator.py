import sys

sys.path.append("hamiltoniansports")
# appending the application dir to sys ensures tests run using the correct relative imports
# and also keep tests out of docker container / application code

import pytest
from unittest.mock import patch, MagicMock
from hamiltoniansports.src.api.abstract import APIAbstract
from hamiltoniansports.src.api.leagues.afl import AFLsquiggleAPI
from hamiltoniansports.src.api.leagues.nrl import NRLsourceAPI
from hamiltoniansports.src.api.creator import APICreator


def test_api_property_not_set():
    """assert usage of hacky 'not yet set' pattern"""
    creator = APICreator()
    with pytest.raises(AttributeError):
        creator.api


def test_assign_api_afl():
    """assert concrete creator class for AFL

    nb. create a new test for each concrete creator class implementation
    """
    creator = APICreator()
    creator.assign_api("afl", "2023")
    # hacky work-around for when classes are not imported using the same namespace
    assert (
        creator.api.__class__.__name__ == AFLsquiggleAPI.__name__
    ), f"Expected class {AFLsquiggleAPI.__name__}, but got {creator.api.__class__.__name__}"


def test_assign_api_nrl():
    """assert concrete creator class for NRL

    nb. create a new test for each concrete creator class implementation
    """
    creator = APICreator()
    creator.assign_api("nrl", "1")
    assert (
        creator.api.__class__.__name__ == NRLsourceAPI.__name__
    ), f"Expected class {NRLsourceAPI.__name__}, but got {creator.api.__class__.__name__}"


def test_assign_api_invalid_league():
    """for invalid leagues"""
    creator = APICreator()
    with pytest.raises(ValueError):
        creator.assign_api("invalid_league", "2023")


def test_populate_from_api_afl():
    """using unittest.mock to test populate_from_api call for AFL.

    nb. create a new test for each concrete creator class implementation
    """
    with patch(
        "src.api.leagues.afl.AFLsquiggleAPI.clear_cache"
    ) as mock_clear_cache, patch(
        "src.api.leagues.afl.AFLsquiggleAPI.get_season_results"
    ) as mock_get_season_results, patch(
        "src.api.leagues.afl.AFLsquiggleAPI.get_team_resources"
    ) as mock_get_team_resources:
        creator = APICreator()
        creator.assign_api("afl", "2023")
        creator.populate_from_api(clearcache=True)

        mock_clear_cache.assert_called_once()
        mock_get_season_results.assert_called_once()
        mock_get_team_resources.assert_called_once()
