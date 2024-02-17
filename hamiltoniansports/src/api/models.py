from pathlib import Path
from pydantic import BaseModel, model_validator
from datetime import datetime
import logging

logger = logging.getLogger("main")


class Team(BaseModel):
    """the team model - api results for the team must be parsed into this format.

    id: int - a unique integer id used to identify that particular team. Does not need to be
    consistent across different seasons, but must be within the same season.
    name: str - the name of the team
    logo_url: str - the url from the team logo to be downloaded
    logo_file: Path - a Path object where the logo will be downloaded to
    """

    id: int
    name: str
    logo_url: str
    logo_file: Path

    def __eq__(self, other: "Team") -> bool:
        """bespoke equality check for testing purposes"""
        if self.id != other.id:
            return False
        if self.name != other.name:
            return False
        if self.logo_url != other.logo_url:
            return False
        if self.logo_file != other.logo_file:
            return False

        return True


class GameResult(BaseModel):
    """individual games, only resultant games are included (ie. no draws / no results etc...)

    winner: int - team id of the winner
    loser: int - team id of the loser
    round: int - the round of this game
    winner_score: int - score of winning team
    loser_score: int - score of losing team
    dt: datetime - datetime of the result

    nb. property attributes made need to change for particular sports where integers do not
    suit scores, or where scorelines are more complex
    """

    winner: int
    loser: int
    round: int
    winner_score: int
    loser_score: int
    dt: datetime

    @model_validator(mode="after")
    def winner_and_loser_must_be_different(self):
        """validation method to ensure that winner and loser are not the same value"""
        if self.winner == self.loser:
            logger.debug(
                f"{self.winner}\n{self.loser}\n{self.round}\n{self.winner_score}\n{self.loser_score}\n{self.dt}"
            )
            raise ValueError("Winner and loser cannot be the same")
        return self

    @model_validator(mode="after")
    def winner_and_loser_scores_must_be_different(self):
        """validation method to ensure that winner score and loser score are not
        the same.
        nb. this may need modification should a sport API be used that has equal
        scores yet another method of score / tie-breaking.
        """
        if self.winner_score == self.loser_score:
            logger.debug(
                f"{self.winner}\n{self.loser}\n{self.round}\n{self.winner_score}\n{self.loser_score}\n{self.dt}"
            )
            raise ValueError("Winner score and loser score cannot be the same")
        return self

    def __eq__(self, other: "GameResult") -> bool:
        """bespoke equality check for testing purposes"""
        if self.winner != other.winner:
            return False
        if self.loser != other.loser:
            return False
        if self.round != other.round:
            return False
        if self.winner_score != other.winner_score:
            return False
        if self.loser_score != other.loser_score:
            return False
        if self.dt != other.dt:
            return False

        return True


class SeasonResults(BaseModel):
    """individual season, with a list of GameResult objects for that season and
    also a list of Team objects that participated in that reason

    league: str - the sports league
    season: str - the season analysed for that sports league
    round_results: dict - a dictionary storing a list of GameResult objects for each round.
    The key is the round. This allows for easy storage / reference.
    teams: dict - a dictionary of Team objects, with the team id used as the key. Again, this
    allows for easy storage / reference
    nrounds: int - dynamic property counts the number of rounds (downloaded so far) for the season
    nteams: int - dynamic property couts the number of teams
    team_ids: list - dynmical property to easily a list of team ids in that season.
    """

    league: str
    season: str
    round_results: dict[int, list[GameResult]]
    teams: dict[int, Team]

    @property
    def nrounds(self) -> int:
        """number of rounds downloaded so far"""
        return len(self.round_results)

    @property
    def nteams(self) -> int:
        """number of teams this season"""
        return len(self.teams)

    @property
    def team_ids(self) -> list[int]:
        """list of team id integers"""
        return list(self.teams.keys())

    def __eq__(self, other: "SeasonResults") -> bool:
        """bespoke equality check for testing purposes"""
        if self.league != other.league or self.season != other.season:
            return False

        if len(self.round_results) != len(other.round_results):
            return False

        # all round results games are equal
        for round, game_results in self.round_results.items():
            if round not in other.round_results:
                return False
            if len(game_results) != len(other.round_results[round]):
                return False
            for game_result in game_results:
                if game_result not in other.round_results[round]:
                    return False

        if len(self.teams) != len(other.teams):
            return False

        # all teams are equal
        for team_id, team in self.teams.items():
            if team_id not in other.teams or team != other.teams[team_id]:
                return False

        return True
