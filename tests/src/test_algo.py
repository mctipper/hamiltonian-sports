import sys

sys.path.append("hamiltoniansports")
# appending the application dir to sys ensures tests run using the correct relative imports
# and also keep tests out of docker container / application code

import pytest
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from unittest.mock import MagicMock, patch, PropertyMock
from hamiltoniansports.src.algo import Algo
from hamiltoniansports.src.api.models import Team, GameResult, SeasonResults


class DummyResults:
    """helper class to create dummy model data for algo / api testing.

    Both positive (hamiltonian cycle possible) and negative (not possible) versions
    can be produced using the boolean flag in the constructor"""

    def __init__(self, positive_case: bool):
        """just build everything during init, its a helper class"""
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
            winner=1,
            loser=2,
            round=1,
            winner_score=3,
            loser_score=2,
            dt=datetime(year=2022, month=2, day=2),
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
        # this game is the only difference between finding a hamilton cycle or not
        self.game_result4 = GameResult(
            winner=3,
            loser=1 if positive_case else 2,
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


def test_algo_initial_values():
    """tests the initial values of Algo class instance are right type/values"""

    dummyresults = DummyResults(positive_case=True)

    algo = Algo(seasonresults=dummyresults.season_results)

    # assert default types
    assert isinstance(algo.adjacency_graph, defaultdict)
    assert isinstance(algo.result_detail, dict)
    assert isinstance(algo.first_hc, list)
    assert isinstance(algo.date_of_first_hc, datetime)
    assert isinstance(algo.all_hc, list)
    assert isinstance(algo.round_hc_tracker, list)
    assert isinstance(algo.permutation_counter, int)
    assert isinstance(algo.round_permutation_tracker, list)
    assert isinstance(algo.algo_seconds_runtime, float)
    assert isinstance(algo.total_hc_found, int)
    assert isinstance(algo.round_of_first_hc, int | None)
    assert isinstance(algo.hc_found, bool)
    assert isinstance(algo.first_hc_team_names, list)
    assert isinstance(algo.hc_season_summary, dict)
    assert isinstance(algo.all_seasons_results_file, Path)

    # assert empty/falsey initial values
    assert not algo.adjacency_graph
    assert not algo.result_detail
    assert not algo.first_hc
    assert not algo.all_hc
    assert not algo.round_hc_tracker
    assert not algo.permutation_counter
    assert not algo.round_permutation_tracker
    assert not algo.total_hc_found
    assert not algo.round_of_first_hc
    assert not algo.hc_found
    assert not algo.first_hc_team_names

    # assert non empty / falsey initial values
    assert algo.date_of_first_hc == datetime(year=2999, month=12, day=31)
    assert algo.seasonresults.season in algo.hc_season_summary
    assert algo.all_seasons_results_file == Path(
        f"./data/{algo.seasonresults.league}/all_seasons.json"
    )


def test_successful_hamiltonian_cycle_search():
    """test the outcome of a (manufactured) successful hamiltonian cycle.
    The outcome is tested by checking attributes in the algo class instance"""
    dr_positive = DummyResults(positive_case=True)
    algo = Algo(seasonresults=dr_positive.season_results)
    algo.hamiltonian_cycle_search()

    # assert values for when a hc was found
    assert algo.first_hc == [1, 2, 3]
    assert algo.date_of_first_hc == datetime(year=2022, month=11, day=11)
    assert algo.all_hc == [[1, 2, 3]]
    assert len(algo.round_hc_tracker) == algo.seasonresults.nrounds
    assert algo.round_hc_tracker == [0, 0, 1]
    assert algo.permutation_counter > 0
    assert len(algo.round_permutation_tracker) == algo.seasonresults.nrounds
    assert algo.round_permutation_tracker == [0, 0, 3]
    assert algo.algo_seconds_runtime > 0
    assert algo.total_hc_found == 1
    assert algo.round_of_first_hc == 3
    assert algo.hc_found
    assert algo.first_hc_team_names == ["Team1", "Team2", "Team3"]
    assert algo.all_seasons_results_file == Path(
        f"./data/{algo.seasonresults.league}/all_seasons.json"
    )


def test_unsuccessful_hamiltonian_cycle_search():
    """test the outcome of a (manufactured) unsuccessful hamiltonian cycle.
    The outcome is tested by checking attributes in the algo class instance"""
    dr_negative = DummyResults(positive_case=False)
    algo = Algo(seasonresults=dr_negative.season_results)
    algo.hamiltonian_cycle_search()

    # assert values for when no hc was found
    assert not algo.first_hc
    assert algo.date_of_first_hc == datetime(year=2999, month=12, day=31)
    assert not algo.all_hc
    assert len(algo.round_hc_tracker) == algo.seasonresults.nrounds
    assert algo.round_hc_tracker == [0] * algo.seasonresults.nrounds
    assert algo.permutation_counter > 0
    assert len(algo.round_permutation_tracker) == algo.seasonresults.nrounds
    assert algo.round_permutation_tracker == [0, 0, 4]
    assert not algo.total_hc_found
    assert not algo.round_of_first_hc
    assert not algo.hc_found
    assert not algo.first_hc_team_names
    assert algo.all_seasons_results_file == Path(
        f"./data/{algo.seasonresults.league}/all_seasons.json"
    )


def test_no_file():
    """test recording of the hamiltonian cycle search results if there is no
    output file existing using mocking.
    """
    dr_negative = DummyResults(positive_case=False)
    algo = Algo(seasonresults=dr_negative.season_results)
    algo.hamiltonian_cycle_search()
    type(algo).all_seasons_results_file = PropertyMock(return_value=MagicMock())
    algo.all_seasons_results_file.is_file.return_value = False

    with patch("builtins.open", new_callable=MagicMock) as mock_open, patch(
        "json.dump", new_callable=MagicMock
    ) as mock_dump:
        mock_open.return_value.__enter__.return_value.read.return_value = "{}"

        algo.save_hc_results_to_file()

        # assert data was written
        mock_open.assert_called_with(algo.all_seasons_results_file, "w")

        # get details of what was written
        last_dump_call_args = mock_dump.call_args[0]
        written_data = last_dump_call_args[0]

        # assert 2022 was written
        assert "2022" in written_data
        # assert that what was written into 2022 matches that in hc_season_summary
        assert written_data["2022"] == algo.hc_season_summary["2022"]


def test_existing_file_no_season_key():
    """test recording of the hamiltonian cycle search results if there is a
    output file existing, but the current season is not found in said file, using mocking.
    """
    dr_negative = DummyResults(positive_case=False)
    algo = Algo(seasonresults=dr_negative.season_results)
    algo.hamiltonian_cycle_search()
    type(algo).all_seasons_results_file = PropertyMock(return_value=MagicMock())
    algo.all_seasons_results_file.is_file.return_value = True

    with patch("builtins.open", new_callable=MagicMock) as mock_open, patch(
        "json.dump", new_callable=MagicMock
    ) as mock_dump:
        mock_open.return_value.__enter__.return_value.read.return_value = '{"2001": {}}'

        algo.save_hc_results_to_file()

        # assert data was written
        mock_open.assert_called_with(algo.all_seasons_results_file, "w")

        # get details of what was written
        last_dump_call_args = mock_dump.call_args[0]
        written_data = last_dump_call_args[0]

        # assert that 2001 exists still
        assert "2001" in written_data
        # assert 2022 has been created
        assert "2022" in written_data
        # assert that what was written into 2022 matches that in hc_season_summary
        assert written_data["2022"] == algo.hc_season_summary["2022"]


def test_existing_file_with_season_key():
    """test recording of the hamiltonian cycle search results if there is a
    output file existing, and the current file exists as a key in it already, using mocking.
    """
    dr_negative = DummyResults(positive_case=False)
    algo = Algo(seasonresults=dr_negative.season_results)
    algo.hamiltonian_cycle_search()
    type(algo).all_seasons_results_file = PropertyMock(return_value=MagicMock())
    algo.all_seasons_results_file.is_file.return_value = True

    with patch("builtins.open", new_callable=MagicMock) as mock_open, patch(
        "json.dump", new_callable=MagicMock
    ) as mock_dump:
        mock_open.return_value.__enter__.return_value.read.return_value = (
            '{"2001": {}, "2022": {}}'
        )

        algo.save_hc_results_to_file()

        # assert data was written
        mock_open.assert_called_with(algo.all_seasons_results_file, "w")

        # get details of what was written
        last_dump_call_args = mock_dump.call_args[0]
        written_data = last_dump_call_args[0]

        # assert that 2001 exists still
        assert "2001" in written_data
        # assert 2022 also exists still
        assert "2022" in written_data
        # assert that what was written into 2022 matches that in hc_season_summary
        assert len(written_data["2022"]) > 0  # not the existing empty one
        assert written_data["2022"] == algo.hc_season_summary["2022"]
