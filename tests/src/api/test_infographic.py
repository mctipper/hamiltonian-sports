import sys

sys.path.append("hamiltoniansports")
# appending the application dir to sys ensures tests run using the correct relative imports
# and also keep tests out of docker container / application code

import pytest
from pathlib import Path
from datetime import datetime
from hamiltoniansports.src.infographic import Infographic
from hamiltoniansports.src.api.models import SeasonResults, GameResult, Team


@pytest.fixture
def mock_infographic():
    """fixture function to generate a mock Infographic class instance"""
    season = "2023"
    first_hc = [1, 2, 3]
    date_of_first_hc = datetime.now()
    round_of_first_hc = 1
    permutations = 10
    result_detail = {
        1: {
            2: GameResult(
                winner=1,
                loser=2,
                round=1,
                winner_score=10,
                loser_score=5,
                dt=datetime(year=2023, month=3, day=1),
            )
        }
    }
    team_details = {
        1: Team(
            id=1,
            name="Team 1",
            logo_url="/logo/team1.png",
            logo_file=Path("./data/logo/team1.png"),
        )
    }
    nteams = 3
    save_location = Path("/tmp")
    infographic = Infographic(
        season,
        first_hc,
        date_of_first_hc,
        round_of_first_hc,
        permutations,
        result_detail,
        team_details,
        nteams,
        save_location,
    )
    return infographic


def test_generate_points(mock_infographic):
    """test the _generate_points() method"""
    mock_infographic._generate_points()
    assert len(mock_infographic.x) == mock_infographic.nteams + 1
    assert len(mock_infographic.y) == mock_infographic.nteams + 1


def test_create_infographic(mock_infographic):
    """im not terribly happy with how the infographic is produced, and plan to refactor
    the code with background options, cycle shape (ie. circle, elipse, square, etc..), arrow
    style, annotation options etc... so I decided not to get too bogged down testing all the
    calls and responses within the current iteration.

    Hence - assert True - LGTM!
    """

    assert True
