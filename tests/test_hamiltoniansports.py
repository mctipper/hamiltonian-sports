import sys

sys.path.append("hamiltoniansports")
# appending the application dir to sys ensures tests run using the correct relative imports
# and also keep tests out of docker container / application code

import pytest
from unittest.mock import patch, Mock, MagicMock, call, PropertyMock
import unittest
from hamiltoniansports.hamiltoniansports import HamiltonianSports, main

# for testing equity
from src.api.creator import APICreator
from src.algo import Algo
from src.infographic import Infographic


class TestHamiltonianSports(unittest.TestCase):
    def setUp(self):
        self.hc = HamiltonianSports(league="afl", season="2023", clearcache=False)

    def test_init(self):
        assert hasattr(self.hc, "league")
        assert hasattr(self.hc, "season")
        assert hasattr(self.hc, "clearcache")
        assert isinstance(self.hc.league, str)
        assert isinstance(self.hc.season, str)
        assert isinstance(self.hc.clearcache, bool)
        assert self.hc.league == "afl"
        assert self.hc.season == "2023"
        assert self.hc.clearcache == False

    def test_basic_call_order(self):
        with pytest.raises(RuntimeError):
            self.hc.populate_from_api()

        with pytest.raises(RuntimeError):
            self.hc.hamiltonian_cycle_search()

        with pytest.raises(RuntimeError):
            self.hc.create_infographic()

        with pytest.raises(RuntimeError):
            self.hc.save_hc_results_to_file()

        with pytest.raises(RuntimeError):
            self.hc.log_season_result()

        with pytest.raises(RuntimeError):
            self.hc.create_infographic()

    def test_api(self):
        # cannot populate from api before api is assigned
        with pytest.raises(RuntimeError):
            self.hc.populate_from_api()

        # test assign_api correctly allocates composition class
        self.hc.assign_api()
        self.assertIsInstance(self.hc.apicreator, APICreator)

        # test populate from api calls correct APICreator method with correct arguments
        with patch.object(self.hc, "apicreator", autospec=True) as mock_apicreator:
            self.hc.populate_from_api()

            mock_apicreator.assign_api.assert_called_once_with(
                league=self.hc.league, season=self.hc.season
            )
            mock_apicreator.populate_from_api.assert_called_once_with(
                clearcache=self.hc.clearcache
            )

    def test_algo(self):
        # cannot populate before assign_api is called
        with pytest.raises(RuntimeError):
            self.hc.assign_algo()

        # generate mocking attribute to allow algo to be set
        mock_apicreator = Mock()
        mock_api = Mock()
        mock_apicreator.api = mock_api

        type(mock_api).seasonresults = PropertyMock(return_value="mocked_value")

        # assign value to .apicreator for mocking
        self.hc.assign_api()

        # cannot run hamiltonian cycle search before assign_algo is called
        with pytest.raises(RuntimeError):
            self.hc.hamiltonian_cycle_search()

        with patch.object(self.hc, "apicreator", new=mock_apicreator):
            self.hc.assign_algo()

            self.assertIsInstance(self.hc.algo, Algo)

            # run mocked algo instance, and check the base method calls the algo method
            with patch.object(self.hc, "algo", autospec=True) as mock_algo:
                self.hc.hamiltonian_cycle_search()
                mock_algo.hamiltonian_cycle_search.assert_called_once()

                self.hc.save_hc_results_to_file()
                mock_algo.save_hc_results_to_file.assert_called_once()

                self.hc.log_season_result()
                mock_algo.log_season_result.assert_called_once()

    def test_infographic(self):
        # cannot design before assign_api is called
        with pytest.raises(RuntimeError):
            self.hc.design_infographic()

        # lots of mocking
        mock_apicreator = Mock()
        mock_api = Mock()
        mock_apicreator.api = mock_api
        type(mock_apicreator.api).team_details = PropertyMock(
            return_value="mocked_value"
        )
        type(mock_apicreator.api).nteams = PropertyMock(return_value="mocked_value")
        type(mock_apicreator.api).save_location = PropertyMock(
            return_value="mocked_value"
        )

        mock_algo = Mock()
        type(mock_algo).first_hc = PropertyMock(return_value="mocked_value")
        type(mock_algo).date_of_first_hc = PropertyMock(return_value="mocked_value")
        type(mock_algo).round_of_first_hc = PropertyMock(return_value="mocked_value")
        type(mock_algo).permutations = PropertyMock(return_value="mocked_value")
        type(mock_algo).result_detail = PropertyMock(return_value="mocked_value")

        # assign value to .apicreator for mocking
        self.hc.assign_api()

        # still cannot run design infographic before assign_algo is called
        with pytest.raises(RuntimeError):
            self.hc.design_infographic()

        with patch.object(self.hc, "apicreator", new=mock_apicreator):
            # assign the value .algo for mocking
            self.hc.assign_algo()

            # cannot run create infographic before design_infographic is called
            with pytest.raises(RuntimeError):
                self.hc.create_infographic()

            with patch.object(self.hc, "algo", new=mock_algo):
                # test composition
                self.hc.design_infographic()

                self.assertIsInstance(self.hc.infographic, Infographic)

                # run mocked infographic instance, and check the base method calls the infographic method
                with patch.object(
                    self.hc, "infographic", autospec=True
                ) as mock_infographic:
                    self.hc.create_infographic()
                    mock_infographic.create_infographic.assert_called_once()
