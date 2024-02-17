import sys

sys.path.append("hamiltoniansports")
# appending the application dir to sys ensures tests run using the correct relative imports
# and also keep tests out of docker container / application code

import pytest
from unittest.mock import patch
from hamiltoniansports.utils.arguments import Arguments


def test_arguments():
    """testing that command-line arguments work as expected"""

    # tests for missing args
    test_args = ["prog"]
    with patch("sys.argv", test_args):
        with pytest.raises(SystemExit):
            _ = Arguments()

    # no league
    test_args = ["prog", "-s", "2000"]
    with patch("sys.argv", test_args):
        with pytest.raises(SystemExit):
            _ = Arguments()

    # no season
    test_args = ["prog", "-l", "afl"]
    with patch("sys.argv", test_args):
        with pytest.raises(SystemExit):
            _ = Arguments()

    # test for valid args
    test_args = ["prog", "-l", "afl", "-s", "2000"]
    with patch("sys.argv", test_args):
        args = Arguments()
        assert args.args.league == "afl"
        assert args.args.season == "2000"

    # test for valid args with clearcache
    test_args = ["prog", "-l", "afl", "-s", "2000", "-c"]
    with patch("sys.argv", test_args):
        args = Arguments()
        assert args.args.clearcache
        assert isinstance(args.args.clearcache, bool)

    # test for invalid league
    test_args = ["prog", "-l", "no_league_ever_like_this", "-s", "2000"]
    with patch("sys.argv", test_args):
        with pytest.raises(SystemExit):
            args = Arguments()

    # test for invalid season
    test_args = ["prog", "-l", "afl", "-s", "no_season_ever_like_this"]
    with patch("sys.argv", test_args):
        with pytest.raises(SystemExit):
            args = Arguments()
