from abc import ABC, abstractmethod
from pathlib import Path
import shutil
import requests
import json
from typing import Any
from src.api.models import SeasonResults

import logging

logger = logging.getLogger("main")


class APIAbstract(ABC):
    """Abstract class for use with the various API classes, as a guide for further usage
    with the API Creator class, which allows for a single class to interact with any API.

    nb. 'json' docs and therefore dict objects are used with these methods, however this
    will need to be modify to suit other document types should additional future APIs
    require it.
    """

    league: str
    season: str | int
    api_url: str
    resource_url: str
    seasonresults: SeasonResults

    @property
    def output_path(self) -> Path:
        """path to where files will be stored locally for this league and season"""
        return Path(f"./data/{self.league}/{self.season}")

    @property
    def season_results_cached_file(self) -> Path:
        """path to where season_results api response file is cached"""
        return self.output_path / "season_results_cache.json"

    @property
    def team_resources_cached_file(self) -> Path:
        """path to where team_resources api response file is cached"""
        return self.output_path / "team_resources_cache.json"

    @staticmethod
    def api_response_helper(url: str, headers: dict) -> Any:
        """helper method to get data from the api

        'Any' is returned to allow for future compatitbility ie. str | dict | list etc...
        """
        response = requests.get(url, headers=headers)
        # response failed
        if response.status_code >= 400:
            raise ValueError(
                f"API request failed with status code {response.status_code}"
            )
        # response redirected, can continue but logging event
        elif response.status_code >= 300:
            logger.info(f"{url} - {response.status_code} - {response.reason}")
        # response successful
        else:
            logger.debug(f"{url} - {response.status_code} - {response.reason}")

        # parse the data depending on the content type
        resp_content_type: str = response.headers["Content-Type"]
        if "json" in resp_content_type:
            # this is the only handled content type currently...
            data = response.json()
        else:
            # default-case will not occur if this code is maintained correctly, raise error as a safety / testing
            raise ValueError(
                f"{response.headers['Content-Type']} is not an implemented api response type"
            )

        return data

    @staticmethod
    def download_helper(url: str, store_filepath: Path) -> None:
        """helper method that first checks if the output exists prior to downloading,
        if the output already exists, no need to download it again

        Also ensures that the filepath exists prior to download
        """
        # check output exists, if so no need to download again
        if not store_filepath.exists():
            # print progress; that gibberish is an escape sequence so that statements dont overlap
            logger.debug(f"Downloading {url}")

            # if the API get request fails for whatever reason, raise it as an exception
            try:
                resp = requests.get(url)
                resp.raise_for_status()
            except requests.exceptions.RequestException as re:
                # the Tarp pattern in __main__ will capture this
                raise re

            if not store_filepath.parent.is_dir():
                store_filepath.parent.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created {store_filepath.parent}")

            with open(store_filepath, mode="wb") as f:
                f.write(resp.content)
                logger.debug(f"Created {store_filepath}")
        else:
            # file is found locally, nothing to do here
            logger.debug(f"Using cached {store_filepath}")

    @staticmethod
    def cache_api_response(data: Any, content_type: str, path: Path) -> None:
        """cache the downloaded data so can be used later if wanted"""
        # this check is a little decoupled due to staticmethod use, could do this better
        valid_content_types = ["json"]
        if content_type not in valid_content_types:
            raise ValueError(
                f"{content_type} is not an implement api response type ({valid_content_types})"
            )

        # supercheck that the parent dir exists
        if not path.parent.is_dir():
            # if not, create it so we have somewhere for the file to go
            path.parent.mkdir(parents=True, exist_ok=True)

        match content_type:
            case "json":
                with open(path, "w") as f:
                    json.dump(data, f, indent=2)
                    logger.debug(f"Cached API response in {path}")
            case _:
                # wont get here if we maintain valid_content_types with this match switch correctly, dupe raise error as a safety
                raise ValueError(
                    f"{content_type} is not an implement api response type ({valid_content_types})"
                )

    @staticmethod
    def load_cached_api_data_helper(path: Path, file_type: str) -> dict:
        """helper method to load a cached file.
        As the only filetype used so-far is json, will return a dict object, but will required
        modification should other API data formats be used later"""

        valid_file_types = ["json"]  # only json built for so far
        if file_type not in valid_file_types:
            raise ValueError(
                f"{file_type} is not an implemented cached file type ({valid_file_types})"
            )

        if not path.exists():
            raise FileNotFoundError(f"Unable to locate cached file {path}")

        with open(path, "r") as f:
            data = json.load(f)
            logger.debug(f"Used cached API response data from {path}")

        return data

    def clear_cache(self) -> None:
        """triggered by an optional cli argument, clears out files/dirs for this particular
        league/season before running any code
        """
        try:
            shutil.rmtree(self.output_path)
            logger.info(f"Cache cleared for {self.league}/{self.season}")
        except FileNotFoundError:
            # it's really no bother if not found, but worth keeping a log in case future behaviours etc...
            logger.debug(
                f"The directory {self.output_path} does not exist - no need to clear cache"
            )

    @abstractmethod
    def _validate_season_for_api(self, season_value: str) -> None:
        """manual checks of api limitations for particular seasons
        any failures in implemented method are to raise appropriate exceptions"""
        raise NotImplementedError(
            f"{self.__class__.__name__}.{__name__} is abstract and has not been implemented in the subclass"
        )

    @abstractmethod
    def _set_headers(self) -> None:
        """set particular headers to be used in the API GET request, updating the self.headers dict appropriately"""
        raise NotImplementedError(
            f"{self.__class__.__name__}.{__name__} is abstract and has not been implemented in the subclass"
        )

    @abstractmethod
    def get_season_results(self):
        """get the season results details from the API, and construct a series of pydantic models
        to store the detail in a simplified way

        This method is required to create a SeasonResults class with composition, and the populate the results by round appropriately
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.{__name__} is abstract and has not been implemented in the subclass"
        )

    @abstractmethod
    def get_team_resources(self):
        """get the 'teams' resources id, name, and logo_url from the API. Expected to also download logos to local storage.
        This method is called after get_season_results, and updates the teams dict of the SeasonResults composition class
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.{__name__} is abstract and has not been implemented in the subclass"
        )
