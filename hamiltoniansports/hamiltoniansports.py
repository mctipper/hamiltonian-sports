from utils.arguments import Arguments
from src.api.creator import APICreator
from src.algo import Algo
from src.infographic import Infographic
import datetime
from utils.logger import Logger

# logging
logger = Logger.setup(current_datetime=datetime.datetime.now())


class HamiltonianSports:
    """This is the main 'client' class, which handles most of the processes via composition, allowing for
    the primary parameters to be easily handled/passed around with minimal input or customisation required for
    further extensions. Also allows for a neater main() with minimalist and clear calls
    """

    # establishing attributes, used by all the composition classes
    league: str
    season: str
    clearcache: bool
    # composition classes
    apicreator: APICreator  # the api connection, creator used to allow different APIs easily
    algo: Algo
    infographic: Infographic

    def __init__(self, league: str, season: str, clearcache: bool) -> None:
        self.league = league
        self.season = season
        self.clearcache = clearcache

    def assign_api(self) -> "HamiltonianSports":
        """initliases an APICreator composition class and assigns the correct API"""
        self.apicreator = APICreator()
        self.apicreator.assign_api(league=self.league, season=self.season)
        return self

    def populate_from_api(self) -> None:
        """uses the provided command line arguments to assign the correct API using composition"""
        if not hasattr(self, "apicreator"):
            raise RuntimeError("populate_from_api() called before assign_api()")
        self.apicreator.populate_from_api(clearcache=self.clearcache)

    def assign_algo(self) -> "HamiltonianSports":
        """assigns the algorithmn using composition.
        Only DFS is used at this stage, but have built it this way to allow other algos in the future maybe.
        """
        if not hasattr(self, "apicreator"):
            raise RuntimeError("assign_algo() called before assign_api()")
        if not hasattr(self.apicreator, "api"):
            raise RuntimeError("assign_algo() called before populate_from_api()")

        self.algo = Algo(seasonresults=self.apicreator.api.seasonresults)

        return self

    def hamiltonian_cycle_search(self) -> None:
        """uses the assigned algorithm to undertake the hamiltonian cycle search"""
        if not hasattr(self, "algo"):
            raise RuntimeError("hamiltonian_cycle_search() called before assign_algo()")
        self.algo.hamiltonian_cycle_search()

    def design_infographic(self) -> "HamiltonianSports":
        """assigns the inforgraphic class using composition"""
        if not hasattr(self, "apicreator"):
            raise RuntimeError("design_infographic() called before assign_api()")
        if not hasattr(self.apicreator, "api"):
            raise RuntimeError("design_infographic() called before populate_from_api()")
        if not hasattr(self, "algo"):
            raise RuntimeError("design_infographic() called before assign_algo()")
        if not self.algo.hc_found:
            raise RuntimeError(
                "design_infographic() called without a valid hamiltonian cycle being found"
            )

        self.infographic = Infographic(
            season=self.season,
            first_hc=self.algo.first_hc,
            date_of_first_hc=self.algo.date_of_first_hc,
            round_of_first_hc=self.algo.round_of_first_hc,
            permutations=self.algo.permutation_counter,
            result_detail=self.algo.result_detail,
            team_details=self.apicreator.api.seasonresults.teams,
            nteams=self.apicreator.api.seasonresults.nteams,
            save_location=self.apicreator.api.output_path,
        )

        return self

    def create_infographic(self) -> None:
        """draws (and stores) the infographic"""
        if not hasattr(self, "infographic"):
            raise RuntimeError(
                "create_infographic() called before design_infographic()"
            )
        self.infographic.create_infographic()

    def save_hc_results_to_file(self) -> None:
        """helper method to save algo results"""
        if not hasattr(self, "algo"):
            raise RuntimeError("save_hc_results_to_file() called before assign_algo()")
        self.algo.save_hc_results_to_file()

    def log_season_result(self) -> None:
        """helper method to log algo results"""
        if not hasattr(self, "algo"):
            raise RuntimeError("log_season_result() called before assign_algo()")
        self.algo.log_season_result()


def main():
    # parse into cli arguments and validate
    av = Arguments()

    # build the client class "hs" (instance of HamiltonianSports) using the validated cli arguments
    hs = HamiltonianSports(
        league=av.args.league, season=av.args.season, clearcache=av.args.clearcache
    )

    # assign the api and get data from it
    hs.assign_api().populate_from_api()

    # assign and run algorithm (will introduce other algorithms for fun later [maybe...])
    hs.assign_algo().hamiltonian_cycle_search()

    # if a result if found, report back and build infographic (if requested)
    if hs.algo.hc_found:
        logger.info("***|||   Hamiltonian Cycle found!   |||***")
        hs.design_infographic().create_infographic()
    else:
        logger.info("No Hamiltonian Cycle Found...")

    # store the results to single file for this league/season
    hs.save_hc_results_to_file()

    # log out some key findings
    hs.log_season_result()


if __name__ == "__main__":
    # Big Tarp logging pattern
    try:
        main()
    except Exception as e:
        logger.exception("Fatal error in main()")
