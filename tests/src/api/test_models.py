import sys

sys.path.append("hamiltoniansports")
# appending the application dir to sys ensures tests run using the correct relative imports
# and also keep tests out of docker container / application code

import pytest
from pathlib import Path
from datetime import datetime
from hamiltoniansports.src.api.models import Team, GameResult, SeasonResults


def test_team_model():
    valid_team_data = {
        "id": 1,
        "name": "Test Team",
        "logo_url": "https://logo.example.com",
        "logo_file": Path("logo.png"),
    }

    team = Team(**valid_team_data)

    # positive test
    # type checking
    assert isinstance(team.id, int)
    assert isinstance(team.name, str)
    assert isinstance(team.logo_url, str)
    assert isinstance(team.logo_file, Path)

    # value checking
    assert team.id == 1
    assert team.name == "Test Team"
    assert team.logo_url == "https://logo.example.com"
    assert team.logo_file == Path("logo.png")

    # negative tests
    # ensure error if any req attributes are missing
    for key in valid_team_data.keys():
        invalid_data = valid_team_data.copy()
        del invalid_data[key]
        with pytest.raises(ValueError):
            Team(**invalid_data)

    # fuzz tests ensuring correct types are passed
    with pytest.raises(ValueError):
        team = Team(
            id="invalid",
            name="Team1",
            logo_url="http://example.com/logo1.png",
            logo_file=Path("/path/to/logo1.png"),
        )

    with pytest.raises(ValueError):
        team = Team(
            id=1,
            name=dict(),
            logo_url="http://example.com/logo1.png",
            logo_file=Path("/path/to/logo1.png"),
        )

    with pytest.raises(ValueError):
        team = Team(
            id=1, name="Team1", logo_url=dict(), logo_file=Path("/path/to/logo1.png")
        )

    with pytest.raises(ValueError):
        team = Team(
            id=1,
            name="Team1",
            logo_url="http://example.com/logo1.png",
            logo_file=dict(),
        )

    with pytest.raises(ValueError):
        team = Team(
            id=1,
            name=True,
            logo_url="invalid_url",
            logo_file=Path("/path/to/logo1.png"),
        )

    with pytest.raises(ValueError):
        team = Team(id=1, name="Team1", logo_url=False, logo_file="invalid_path")

    # test equality
    assert Team(
        id=1,
        name="Team1",
        logo_url="http://example.com/logo1.png",
        logo_file=Path("/path/to/logo1.png"),
    ) == Team(
        id=1,
        name="Team1",
        logo_url="http://example.com/logo1.png",
        logo_file=Path("/path/to/logo1.png"),
    )
    assert not Team(
        id=1,
        name="Team1",
        logo_url="http://example.com/logo1.png",
        logo_file=Path("/path/to/logo1.png"),
    ) == Team(
        id=2,
        name="Team1",
        logo_url="http://example.com/logo1.png",
        logo_file=Path("/path/to/logo1.png"),
    )
    assert not Team(
        id=1,
        name="Team1",
        logo_url="http://example.com/logo1.png",
        logo_file=Path("/path/to/logo1.png"),
    ) == Team(
        id=1,
        name="Team2",
        logo_url="http://example.com/logo1.png",
        logo_file=Path("/path/to/logo1.png"),
    )
    assert not Team(
        id=1,
        name="Team1",
        logo_url="http://example.com/logo1.png",
        logo_file=Path("/path/to/logo1.png"),
    ) == Team(
        id=1,
        name="Team1",
        logo_url="http://example.com/logo2.png",
        logo_file=Path("/path/to/logo1.png"),
    )
    assert not Team(
        id=1,
        name="Team1",
        logo_url="http://example.com/logo1.png",
        logo_file=Path("/path/to/logo1.png"),
    ) == Team(
        id=1,
        name="Team1",
        logo_url="http://example.com/logo1.png",
        logo_file=Path("/path/to/logo2.png"),
    )


def test_game_result_model():
    cur_dt = datetime.now()  # set once to ensure __eq__ can be tested
    valid_data = {
        "winner": 1,
        "loser": 2,
        "round": 3,
        "winner_score": 4,
        "loser_score": 2,
        "dt": cur_dt,
    }

    game_result = GameResult(**valid_data)

    # positive test
    # type checking
    assert isinstance(game_result.winner, int)
    assert isinstance(game_result.loser, int)
    assert isinstance(game_result.round, int)
    assert isinstance(game_result.winner_score, int)
    assert isinstance(game_result.loser_score, int)
    assert isinstance(game_result.dt, datetime)

    # value checking
    assert game_result.winner == 1
    assert game_result.loser == 2
    assert game_result.round == 3
    assert game_result.winner_score == 4
    assert game_result.loser_score == 2
    assert game_result.dt == cur_dt

    # negative tests
    # ensure error if any req attributes are missing
    for key in valid_data.keys():
        invalid_data = valid_data.copy()
        del invalid_data[key]
        with pytest.raises(ValueError):
            GameResult(**invalid_data)

    # complains when winner == loser
    with pytest.raises(ValueError):
        game_result = GameResult(
            winner=1, loser=1, round=1, winner_score=3, loser_score=2, dt=cur_dt
        )

    # complains when winner_score == loser_score
    with pytest.raises(ValueError):
        game_result = GameResult(
            winner=1, loser=2, round=1, winner_score=3, loser_score=3, dt=cur_dt
        )

    # fuzz tests ensuring correct types are passed
    with pytest.raises(ValueError):
        game_result = GameResult(
            winner="invalid", loser=2, round=1, winner_score=3, loser_score=2, dt=cur_dt
        )

    with pytest.raises(ValueError):
        game_result = GameResult(
            winner=1, loser="invalid", round=1, winner_score=3, loser_score=2, dt=cur_dt
        )

    with pytest.raises(ValueError):
        game_result = GameResult(
            winner=1, loser=2, round="invalid", winner_score=3, loser_score=2, dt=cur_dt
        )

    with pytest.raises(ValueError):
        game_result = GameResult(
            winner=1, loser=2, round=1, winner_score="invalid", loser_score=2, dt=cur_dt
        )

    with pytest.raises(ValueError):
        game_result = GameResult(
            winner=1, loser=2, round=1, winner_score=3, loser_score="invalid", dt=cur_dt
        )

    with pytest.raises(ValueError):
        game_result = GameResult(
            winner=1, loser=2, round=1, winner_score=3, loser_score=2, dt="invalid"
        )

    with pytest.raises(ValueError):
        game_result = GameResult(
            winner=1, loser=2, round=1, winner_score=3, loser_score=2, dt=dict()
        )

    # test equality
    assert GameResult(
        winner=1, loser=2, round=1, winner_score=3, loser_score=2, dt=cur_dt
    ) == GameResult(
        winner=1, loser=2, round=1, winner_score=3, loser_score=2, dt=cur_dt
    )
    assert not GameResult(
        winner=1, loser=2, round=1, winner_score=3, loser_score=2, dt=cur_dt
    ) == GameResult(
        winner=3, loser=2, round=1, winner_score=3, loser_score=2, dt=cur_dt
    )
    assert not GameResult(
        winner=1, loser=2, round=1, winner_score=3, loser_score=2, dt=cur_dt
    ) == GameResult(
        winner=1, loser=3, round=1, winner_score=3, loser_score=2, dt=cur_dt
    )
    assert not GameResult(
        winner=1, loser=2, round=1, winner_score=3, loser_score=2, dt=cur_dt
    ) == GameResult(
        winner=1, loser=2, round=3, winner_score=3, loser_score=2, dt=cur_dt
    )
    assert not GameResult(
        winner=1, loser=2, round=1, winner_score=3, loser_score=2, dt=cur_dt
    ) == GameResult(
        winner=1, loser=2, round=1, winner_score=4, loser_score=2, dt=cur_dt
    )
    assert not GameResult(
        winner=1, loser=2, round=1, winner_score=3, loser_score=2, dt=cur_dt
    ) == GameResult(
        winner=1, loser=2, round=1, winner_score=3, loser_score=4, dt=cur_dt
    )
    assert not GameResult(
        winner=1, loser=2, round=1, winner_score=3, loser_score=2, dt=cur_dt
    ) == GameResult(
        winner=1,
        loser=2,
        round=1,
        winner_score=3,
        loser_score=2,
        dt=datetime(year=2000, month=9, day=1),
    )


def test_season_results_model():
    cur_dt = datetime.now()  # set once to ensure __eq__ can be tested
    team1 = Team(
        id=1,
        name="Team1",
        logo_url="http://example.com/logo1.png",
        logo_file=Path("/path/to/logo1.png"),
    )
    team2 = Team(
        id=2,
        name="Team2",
        logo_url="http://example.com/logo2.png",
        logo_file=Path("/path/to/logo2.png"),
    )
    game_result = GameResult(
        winner=1, loser=2, round=1, winner_score=3, loser_score=2, dt=cur_dt
    )

    valid_data = {
        "league": "TestLeague",
        "season": "2022",
        "round_results": {1: [game_result]},
        "teams": {1: team1, 2: team2},
    }

    season_results = SeasonResults(**valid_data)

    # positive test
    # type checking
    assert isinstance(season_results.league, str)
    assert isinstance(season_results.season, str)
    assert isinstance(season_results.round_results, dict)
    assert all(isinstance(key, int) for key in season_results.round_results.keys())
    assert all(
        isinstance(value, list) for value in season_results.round_results.values()
    )
    assert all(
        isinstance(item, GameResult)
        for value in season_results.round_results.values()
        for item in value
    )
    assert isinstance(season_results.teams, dict)
    assert all(isinstance(key, int) for key in season_results.teams.keys())
    assert all(isinstance(value, Team) for value in season_results.teams.values())
    assert isinstance(season_results.nrounds, int)
    assert isinstance(season_results.nteams, int)
    assert isinstance(season_results.team_ids, list)
    assert all(isinstance(team_id, int) for team_id in season_results.team_ids)

    # value checking
    assert season_results.league == "TestLeague"
    assert season_results.season == "2022"
    assert season_results.round_results == {1: [game_result]}
    assert season_results.teams == {1: team1, 2: team2}
    assert season_results.nrounds == len(season_results.round_results)
    assert season_results.nteams == len(season_results.teams)
    assert season_results.team_ids == list(season_results.teams.keys())

    # negative tests
    # ensure error if any req attributes are missing
    for key in valid_data.keys():
        invalid_data = valid_data.copy()
        del invalid_data[key]
        with pytest.raises(ValueError):
            SeasonResults(**invalid_data)

    # fuzz tests ensure correct types are passed
    with pytest.raises(ValueError):
        season_results = SeasonResults(
            league=dict(),
            season="2022",
            round_results={1: [game_result]},
            teams={1: team1, 2: team2},
        )

    with pytest.raises(ValueError):
        season_results = SeasonResults(
            league="TestLeague",
            season=dict(),
            round_results={1: [game_result]},
            teams={1: team1, 2: team2},
        )

    with pytest.raises(ValueError):
        season_results = SeasonResults(
            league="TestLeague",
            season="2022",
            round_results=1,
            teams={1: team1, 2: team2},
        )

    with pytest.raises(ValueError):
        season_results = SeasonResults(
            league="TestLeague",
            season="2022",
            round_results={1: [game_result]},
            teams=2,
        )

    with pytest.raises(ValueError):
        season_results = SeasonResults(
            league="TestLeague",
            season="2022",
            round_results={1: [1, 2, 3]},
            teams={1: team1, 2: team2},
        )

    # variety of round_results fuzz tests
    with pytest.raises(TypeError):
        season_results = SeasonResults(
            league="TestLeague",
            season="2022",
            round_results={game_result: [1]},
            teams={1: team1, 2: team2},
        )

    with pytest.raises(TypeError):
        season_results = SeasonResults(
            league="TestLeague",
            season="2022",
            round_results={game_result: [game_result]},
            teams={1: team1, 2: team2},
        )

    with pytest.raises(ValueError):
        season_results = SeasonResults(
            league="TestLeague",
            season="2022",
            round_results={1: game_result},
            teams={1: team1, 2: team2},
        )

    # variety of teams fuzz tests
    with pytest.raises(TypeError):
        season_results = SeasonResults(
            league="TestLeague",
            season="2022",
            round_results={1: [game_result]},
            teams={team1: 1, team2: 1},
        )

    with pytest.raises(ValueError):
        season_results = SeasonResults(
            league="TestLeague",
            season="2022",
            round_results={1: [game_result]},
            teams={1: [team1, team2]},
        )

    with pytest.raises(ValueError):
        season_results = SeasonResults(
            league="TestLeague",
            season="2022",
            round_results={1: [game_result]},
            teams=[team1, team2],
        )

    with pytest.raises(TypeError):
        season_results = SeasonResults(
            league="TestLeague",
            season="2022",
            round_results={1: [game_result]},
            teams=set(team1, team2),
        )

    # equality
    season_results_orig = SeasonResults(**valid_data)
    season_results_other = SeasonResults(**valid_data)
    assert season_results_orig == season_results_other

    diff_league_data = {
        "league": "DifferentLeague",
        "season": "2022",
        "round_results": {1: [game_result]},
        "teams": {1: team1, 2: team2},
    }

    assert not season_results == SeasonResults(**diff_league_data)

    diff_season_data = {
        "league": "TestLeague",
        "season": "2000",
        "round_results": {1: [game_result]},
        "teams": {1: team1, 2: team2},
    }

    assert not season_results_orig == SeasonResults(**diff_season_data)
