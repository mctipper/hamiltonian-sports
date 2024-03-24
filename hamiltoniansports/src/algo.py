import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from src.api.models import SeasonResults, GameResult
import time
import logging

logger = logging.getLogger("main")


class Algo:
    """class used for running the algorithm seasing for a Hamiltonian Cycle and
    miscellious results / data related to it"""

    def __init__(self, seasonresults: SeasonResults):
        self.seasonresults: SeasonResults = seasonresults

        self.adjacency_graph: defaultdict[int, set[int]] = defaultdict()
        self.result_detail: dict[int, dict[int, GameResult]] = dict()
        self.first_hc: list[int] = []
        # purposefully large datetime to ensure first hamiltonian cycle is below this date
        self.date_of_first_hc: datetime = datetime(year=2999, month=12, day=31)
        self.all_hc: list[list] = []
        self.round_hc_tracker: list[int] = []
        self.permutation_counter: int = 0
        self.round_permutation_tracker: list[int] = []
        self.algo_seconds_runtime: float = 0.0

    @property
    def total_hc_found(self) -> int:
        return len(self.all_hc)

    @property
    def round_of_first_hc(self) -> int | None:
        """index+1 of first non-zero in list"""
        return next(
            (
                index + 1
                for index, value in enumerate(self.round_hc_tracker)
                if value != 0
            ),
            None,
        )

    @property
    def hc_found(self) -> bool:
        """superfluous, however allows for easier comprehension when checking if a
        hamiltonian cycle has been found
        """
        if self.first_hc:
            return True
        else:
            return False

    @property
    def first_hc_team_names(self) -> list[str]:
        """uses the first_hc list of team ids to create the same but with team names instead"""
        if not self.first_hc:
            # no hamiltonian cycle found OR search not run; either way return an empty list
            return []
        else:
            return [self.seasonresults.teams[team_id].name for team_id in self.first_hc]

    @property
    def hc_season_summary(
        self,
    ) -> dict[str, dict[str, list | int | float | datetime | None]]:
        """helper-property to return a dict of the key hamiltonian cycle details, just simplifies logging"""
        return {
            self.seasonresults.season: {
                "Has_HC": 1 if self.hc_found else 0,
                "HC": self.first_hc,
                "HC_Team_Names": self.first_hc_team_names,
                "HC_Round": self.round_of_first_hc,
                "HC_Date": self.date_of_first_hc,
                "Permutations": self.permutation_counter,
                "Permutation_Progression": self.round_permutation_tracker,
                "Algo_Runtime_s": self.algo_seconds_runtime,
                "Algo_Runtime_m": self.algo_seconds_runtime / 60,
                "Total_HC": self.total_hc_found,
            }
        }

    @property
    def all_seasons_results_file(self) -> Path:
        """path of the file containing all the hamiltonian cycles search results for each season"""
        return Path(f"./data/{self.seasonresults.league}/all_seasons.json")

    def log_season_result(self) -> None:
        """log the contents of the single_season_result dict, just as an FYI on progress"""
        for k, v in self.hc_season_summary.items():
            logger.info(f"Season: {k}")
            for k1, v1 in v.items():
                logger.info(f"{k1}: {v1}")
        logger.info(f"END\n")

    def save_hc_results_to_file(self) -> None:
        """append / replace this seasons results to a single file."""
        # checks for existence, if not then create
        if not self.all_seasons_results_file.parent.is_dir():
            self.all_seasons_results_file.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"{self.all_seasons_results_file} created")
        if not self.all_seasons_results_file.is_file():
            # if the file doesnt yet exist, create an empty json doc
            with open(self.all_seasons_results_file, "w") as f:
                json.dump({}, f)
                logger.debug(
                    f"Empty json doc created at {self.all_seasons_results_file}"
                )

        with open(self.all_seasons_results_file, "r") as f:
            all_season_results = json.load(f)
            logger.debug(f"Loaded all_season_results file")

        # season to be appended / replaced
        season: str = next(iter(self.hc_season_summary))

        # check if season already in the file, if so delete it
        if season in all_season_results:
            del all_season_results[season]
            logger.debug(f"Deleted season {season} from file")

        # insert the season into the file
        all_season_results[season] = self.hc_season_summary[season]
        logger.debug(f"Inserted season {season} into file")

        # save the newly updated file
        with open(self.all_seasons_results_file, "w") as f:
            json.dump(all_season_results, f, indent=2, default=str)
            logger.debug(f"Exported all_season_results to file")

    def _hamiltonian_cycle_permutation_logger(self) -> None:
        """helper function to log permutation progress, just helpful for eyeballing/ensuring compute is progressing"""
        thresholds = [10, 100, 1000, 10000, 100000, 500000, 1000000]

        if self.permutation_counter > thresholds[-1]:
            if self.permutation_counter % 1000000 == 0:
                logger.info(f"{self.permutation_counter} permutations")
        else:
            for threshold in thresholds:
                if self.permutation_counter < threshold * 10:
                    if self.permutation_counter % threshold == 0:
                        logger.info(f"{self.permutation_counter} permutations")
                    break

    def _find_hamiltonian_cycle(self, hc_length_target: int):
        """housing method to setup and then cur recursive algo"""

        def dfs(cur_team: int, path: list[int]) -> bool | None:
            """recursive dfs algo"""
            self._hamiltonian_cycle_permutation_logger()
            # check if we have a full length path
            if len(path) == len(self.adjacency_graph) == hc_length_target:
                # check if we have a hamiltonian cycle, but looking if the first team in the current
                # path was defeated by the last team in the current path
                if path[0] in [t for t in self.adjacency_graph[cur_team]]:
                    # append the hc to list of all hcs found, because stats
                    self.all_hc.append(path.copy())
                    # get all date details to allow for a check if this is the 'first occuring' hc
                    hc_dates: list = []
                    # check dt for last on path and first on path
                    hc_dates.append(self.result_detail[path[-1]][path[0]].dt)
                    # check dt for all other winner/loser combos in the hc
                    for i in range(1, hc_length_target, 1):
                        w = path[i - 1]
                        l = path[i]
                        hc_dates.append(self.result_detail[w][l].dt)
                    # get the max date, which is when the hamiltonian cycle was apparant
                    max_hc_date = max(hc_dates)
                    # update first_hc and its date if the current permutation is earlier
                    if max_hc_date < self.date_of_first_hc:
                        self.date_of_first_hc = max_hc_date
                        self.first_hc = path.copy()
                # return None to allow exit and backtracking to occur
                return

            # the main DFS callstack recursion loop
            # using the 'current team', check if each defeated team is currently in the
            # graph traversal 'path', recursively calling until the end of the path is
            # reached or a hamiltonian cycle is found
            if (
                cur_team in self.adjacency_graph
            ):  # check adjacency graph first as a safety
                defeated_teams = self.adjacency_graph[cur_team]
                for next_team in defeated_teams:
                    if next_team not in path:
                        self.permutation_counter += 1
                        path.append(next_team)
                        if dfs(next_team, path):
                            return True
                        # if DFS determines the path is at the end (either as a hamiltonian cycle
                        # or a dead-end), remove the last item and continue down the call stack
                        path.pop()

            # hit the end of recursion calls here
            return False

        # initial prep work, select the first team in the adjacency_graph
        # and make the first call of recursive algo method
        logger.debug("Begin recursion")
        start_time = time.perf_counter()  # start a timer because stats
        cur_team = next(iter(self.adjacency_graph))
        dfs(cur_team=cur_team, path=[cur_team])

        # once the recursive calls are all done, log the time it took
        self.algo_seconds_runtime += time.perf_counter() - start_time
        logger.debug(f"End recursion - {self.algo_seconds_runtime} seconds")

    def hamiltonian_cycle_search(self) -> None:
        """primary search method which builds the adjacency graph incrementally by round, and then
        triggers the the Hamiltonian Cycle search.

        nb. the method name hamiltonian_cycle_search was used in case other algorithms are used in the future, however
        only DFS is used at this stage. Will need a minor refactor to introduce other algorithm options.
        """
        # logging progress
        logger.info(f"Season {self.seasonresults.season}")

        # initialise empty adjacency graph
        for i in self.seasonresults.team_ids:
            self.adjacency_graph[i] = set()

        # the main round-by-round loop, building the adjacency graph based on results
        # up-to that round, and run the _find_hamiltonian_cycle method for each in-sequence
        for cur_round in self.seasonresults.rounds_list:
            logger.info(f"Searching round {cur_round}...")
            team_w_no_loss_yet: bool = False
            cur_round_results: list[GameResult] = self.seasonresults.round_results[
                cur_round
            ]
            for cur_game in cur_round_results:
                # check if winner listed in adjacency graph yet
                if cur_game.winner not in self.adjacency_graph:
                    self.adjacency_graph[cur_game.winner] = set()
                # update adjacency_graph, only if first time winner-loser combo
                if cur_game.loser not in self.adjacency_graph[cur_game.winner]:
                    self.adjacency_graph[cur_game.winner].add(cur_game.loser)
                    if len(self.adjacency_graph[cur_game.winner]) == cur_round:
                        # the number of losers against the current winner equals the number of rounds
                        # indicates that this team is yet to lose
                        team_w_no_loss_yet = True
                    # update results_matrix (which is a dict for simple referal for game_details, used later)
                    if cur_game.winner not in self.result_detail:
                        # was getting nested typehinting complaints with defaultdict, hence this work-around
                        self.result_detail[cur_game.winner] = {}
                    self.result_detail[cur_game.winner][cur_game.loser] = cur_game

            # check if hc is possible (ie. all teams both won and lost) before running
            if (
                len(self.adjacency_graph) < self.seasonresults.nteams
                or team_w_no_loss_yet
            ):
                # if there are any teams not yet in the adjacency_graph that means they are yet to win
                logger.info(f"Hamiltonian Cycle not possible in round {cur_round}")
            else:
                # run the hamiltonian cycle checking algo
                self._find_hamiltonian_cycle(hc_length_target=self.seasonresults.nteams)

            # update trackers
            self.round_permutation_tracker.append(self.permutation_counter)
            self.round_hc_tracker.append(self.total_hc_found)

            # if a hamiltonian cycle was found this round, break the for-loop since we dont
            # need to look into further rounds. (nb. can comment this out to continue searching,
            # finding all Hamiltonian Cycles within an entire season... but yeah compute can explode... )
            if self.first_hc:
                break
