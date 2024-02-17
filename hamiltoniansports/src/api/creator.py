from src.api.abstract import APIAbstract
from typing import Optional

import logging

logger = logging.getLogger("main")


class APICreator:
    """Creator class for interacting with the particular league (and season) API requested.
    Ensures the main script is able to extract, search, generate artifacts regardless of the
    sports league or season.

    Uses composition for interacting with the correct API
    """

    def __init__(self):
        # purposeful
        pass

    @property
    def api(self):
        """Allowing a hacky 'not yet set' pattern here"""
        if not hasattr(self, "_api"):
            raise AttributeError("API has not been assigned to this creator")
        return self._api

    def assign_api(self, league: str, season: str) -> None:
        """composition class _api used to assign the correct api to the api variable.
        API classes are only imported when required

        Preferred this usage rather than _api.setter decorate as am passing in two variables
        and using tuple-splitting just adds a layer of smell imo"""
        match league:
            case "afl":
                from src.api.leagues.afl import AFLsquiggleAPI

                self._api = AFLsquiggleAPI(league=league, season_str=season)

            case "nrl":
                from src.api.leagues.nrl import NRLsourceAPI

                self._api = NRLsourceAPI(league=league, season=season)

            case _:
                # should never occur when command line arguments are validated properly
                raise ValueError(
                    f'Unable to compose api based on league_value "{league}"'
                )

    def populate_from_api(self, clearcache: bool = False) -> None:
        """calls all the get_ methods, includes optionally calling the clear_cache method to
        remove any previously downloaded files prior to downloading them now.
        Enforces calling of get_season_results before get_team_resources."""
        if clearcache:
            # the cache is cleared only at this step, right before any new data is pulled
            self.api.clear_cache()
        self.api.get_season_results()
        self.api.get_team_resources()
        logger.debug(f"All API get operations completed")
