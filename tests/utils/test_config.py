import sys

sys.path.append("hamiltoniansports")
# appending the application dir to sys ensures tests run using the correct relative imports
# and also keep tests out of docker container / application code

import pytest
from hamiltoniansports.utils.config import Config


def test_config():
    """test prescence and type of config attributes and properties"""
    config = Config()

    # required methods and properties
    assert hasattr(config, "email"), "Config object requires an 'email' attribute"
    assert hasattr(
        config, "valid_leagues_seasons"
    ), "Config object requires a 'valid_leagues_seasons' attribute"
    assert hasattr(
        config, "valid_seasons"
    ), "Config object requires a 'valid_seasons' attribute"

    assert isinstance(config.email, str), "'email' attribute should be a string"
    assert isinstance(
        config.valid_leagues_seasons, dict
    ), "'valid_leagues_seasons' attribute should be a dictionary"

    # check that valid seasons returns KeyError for invalid / empty input
    with pytest.raises(KeyError):
        config.valid_seasons("")

    with pytest.raises(KeyError):
        config.valid_seasons("there_is_no_league_in_the_world_name_like_this")
