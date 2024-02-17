import argparse
from utils.config import Config
import logging

logger = logging.getLogger("main")


class ValidateSeason(argparse.Action):
    """custom validator for 'season' arguments based on value of 'league' entered"""

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str,
        option_string=None,
    ):
        league = getattr(namespace, "league")
        if (
            league in Config.valid_leagues_seasons
            and values in Config.valid_leagues_seasons[league]
        ):
            setattr(namespace, self.dest, values)
        else:
            parser.error(f"Invalid season '{values}' for league '{league}'")


class Arguments:
    """class to handle definition, validation, and parsing of command line arguments"""

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="League and season arguments")
        self.parser.add_argument(
            "-l",
            "--league",
            type=str,
            required=True,
            choices=Config.valid_leagues_seasons.keys(),
            help="Sports league to be assessed",
        )
        self.parser.add_argument(
            "-s",
            "--season",
            type=str,
            required=True,
            action=ValidateSeason,
            help="Season/Year to be assessed. Must match synatx for league",
        )
        self.parser.add_argument(
            "-c",
            "--clearcache",
            action="store_true",
            help="Clear cached files/resources for this league/season",
        )

        self.args = self.parser.parse_args()
        logger.debug(f"Command line arguments parsed\n{self.args}")
