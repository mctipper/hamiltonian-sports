from src.api.abstract import APIAbstract
from pathlib import Path
from datetime import datetime
from utils.config import Config
from src.api.models import SeasonResults, GameResult, Team

import logging

logger = logging.getLogger("main")


class AFLsquiggleAPI(APIAbstract):
    """The API contrete class for using the AFL "Squiggle" API, kindly made available free
    by @SquiggleAFL https://squiggle.com.au/ and https://api.squiggle.com.au/
    Be sure to read the 'How To Be Nice' section and show appreciation for what Squiggle has set up
    """

    league: str
    season: int
    headers: dict[str, str]
    api_url: str
    resource_url: str
    seasonresults: SeasonResults

    def __init__(self, league: str, season_str: str):
        self.league = league
        self.api_url = "https://api.squiggle.com.au/"
        self.resource_url = "https://squiggle.com.au"
        self._validate_season_for_api(season_str)
        self._set_headers()

    def _validate_season_for_api(self, season_str: str) -> None:
        """validates the season value further for this particular API, as different league
        APIs might be structured differently. While the Arguments() args parsing should be handling
        this already, including it here again since we may have some really bespoke season validation
        rules for other APIs.

        This also assign self.season as an integer, different from the supplied/default typing
        of season being a str
        """
        self.season = int(season_str)
        min_year: int = int(Config.valid_leagues_seasons["afl"][0])
        max_year: int = int(Config.valid_leagues_seasons["afl"][-1])
        if not min_year <= self.season <= max_year:
            raise ValueError(
                f'{self.league} season value "{self.season}" outside of valid range [{min_year}, {max_year}]'
            )
        logger.debug('"Season" argument validated for Squiggle API')

    def _set_headers(self) -> None:
        """set particular headers to be used in the API GET request, updating the self.headers dict appropriately"""
        if Config.email == "dummy@email.com":
            logger.warning(f"Please update your email address in ./utils/config.py")
        self.headers = {"User-Agent": Config.email}
        if not self.headers["User-Agent"]:
            raise ValueError("Please enter your email address in config.py")

    def get_season_results(self) -> None:
        """get the season results details from the API, and construct a series of pydantic models
        to store the detail in a simplified way"""
        # create initial composition class
        self.seasonresults = SeasonResults(
            league=self.league, season=str(self.season), round_results={}, teams={}
        )

        # if the cached file from a previous run doesnt exist, then get the data from the api
        if self.season_results_cached_file.exists():
            season_result_data = self.load_cached_api_data_helper(
                path=self.season_results_cached_file, file_type="json"
            )
            logger.debug("Loaded season_results from cache")
        else:
            season_result_data = self.api_response_helper(
                url=f"{self.api_url}?q=games;year={str(self.season)}",
                headers=self.headers,
            )
            logger.debug("Loaded season_results from API")
            self.cache_api_response(
                data=season_result_data,
                content_type="json",
                path=self.season_results_cached_file,
            )
            logger.debug("Cached API response for season_results")

        # loop through the game results returned, creating a model for each game and round

        # the results for each round are stored in a dictionary, as results are not guarenteed to be
        # returned sequentially in round-order, the ensures round/games are correctly grouped together
        round_results: dict[int, list[GameResult]] = {}

        for game in season_result_data["games"]:
            round: int = int(game["round"])
            # add the empty round value, in case there happen to be no winners this round
            if round not in round_results:
                round_results[round] = []

            if game["hscore"] == game["ascore"]:
                # it's a draw both the teams are even
                continue
            # assign the key data points from the api response into the variables
            winner: int = int(game["winnerteamid"])
            loser: int = int(
                game["hteamid"] if winner == game["ateamid"] else game["ateamid"]
            )
            winner_score: int = int(
                game["hscore"] if winner == game["hteamid"] else game["ascore"]
            )
            loser_score: int = int(
                game["hscore"] if winner != game["hteamid"] else game["ascore"]
            )
            datetime_str: str = game["date"]
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

            cur_game = GameResult(
                winner=winner,
                loser=loser,
                round=round,
                winner_score=winner_score,
                loser_score=loser_score,
                dt=dt,
            )

            # appending the game results to a list for each round
            round_results[round].append(cur_game)

        # update the season results
        self.seasonresults.round_results = round_results

        logger.debug("Appended all game results")

    def get_team_resources(self) -> None:
        """get the 'teams' resources id, name, and logo_url from the API. Will download logos to local storage."""

        # team data validation requires seasonresults to be downloaded / processed first
        if not hasattr(self, "seasonresults"):
            raise RuntimeError(
                "get_team_resources function called before get_season_results - amend method call order"
            )

        # if the cached file from a previous run doesnt exist, then get the data from the api
        if self.team_resources_cached_file.exists():
            team_data = self.load_cached_api_data_helper(
                path=self.team_resources_cached_file, file_type="json"
            )
            logger.debug("Loaded team_data from cache")
        else:
            team_data = self.api_response_helper(
                url=f"{self.api_url}?q=teams;year={str(self.season)}",
                headers=self.headers,
            )
            logger.debug("Loaded team_data from API")

            self.cache_api_response(
                data=team_data,
                content_type="json",
                path=self.team_resources_cached_file,
            )
            logger.debug("Cached API response for team_data")

        # in the squiggle api, teams are returned for that particular season if within the founded-retired
        # values, even if they did not play any games that season (e.g. the war years), this check ensures
        # that only teams that played that season are included
        teams_with_results = set()
        for _, game_results in self.seasonresults.round_results.items():
            for game_result in game_results:
                teams_with_results.add(game_result.winner)
                teams_with_results.add(game_result.loser)

        for team in team_data["teams"]:
            team_id: int = int(team["id"])
            if team_id in teams_with_results:
                # only create a team object if results were found for that team this year
                cur_team = Team(
                    id=team_id,
                    name=team["name"],
                    logo_url=f'{self.resource_url}{team["logo"]}',
                    logo_file=Path(f'{self.output_path}/logos/{team["name"]}.png'),
                )

                # download the image
                self.download_helper(
                    url=cur_team.logo_url, store_filepath=cur_team.logo_file
                )

                # append to seasonresults model
                self.seasonresults.teams[team_id] = cur_team

                logger.debug(f"Appended {cur_team}")
            else:
                logger.debug(f'Excluded {team["name"]} from season {self.season}')
