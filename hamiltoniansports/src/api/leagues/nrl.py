from src.api.abstract import APIAbstract
from src.api.models import SeasonResults


class NRLsourceAPI(APIAbstract):
    """DO NOT USE
    This is not yet implemented, just a placeholder / pseudocode situation for now, for testing purposes
    """

    league: str
    season: int
    headers: dict
    api_url: str
    resource_url: str
    seasonresults: SeasonResults

    def __init__(self, league: str, season: str):
        print("nrl api init called")
        self.league = league
        self.api_url = "TBD"
        self.resource_url = "TBD"
        self._validate_season_for_api(season)
        self._set_headers()
        self.seasonresults = SeasonResults(
            league=league, season=str(season), round_results={}, teams={}
        )

    def _validate_season_for_api(self, season: str) -> None:
        """validates the season value further for this particular API, as different league
        APIs might be structured differently
        """
        try:
            self.season = int(season)
            min_year: int = 0  # purposefully set low to remind of non-implementation
            max_year: int = 1  # purposefully set low to remind of non-implementation
            if not min_year <= self.season <= max_year:
                raise ValueError(
                    f'{self.league} season value "{self.season}" outside of valid range [{min_year}, {max_year}]'
                )
        except ValueError as ve:
            print(
                f"{ve}\n{self.season} is an invalid season format for API, required an integer within range"
            )
            raise

    def _set_headers(self) -> None:
        """ """
        self.headers = {}

    def get_team_resources(self):
        """using composition build a model of the teams, including id, nickname and the logo"""
        pass

    def get_season_results(self):
        """ """
        pass
