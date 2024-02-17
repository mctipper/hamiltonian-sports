import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from src.api.models import GameResult, Team
from pathlib import Path

import logging

logger = logging.getLogger("main")


class Infographic:
    """class to draw the infographic of the first hamiltonian cycle found for that season.
    The infographic is a circle of teams in order completing the cycle, with some basic game
    result details and some other details about the hamiltonian cycle. The infographic is purposefully
    basic, will have a go at making it look smarter later.

    The class constucter takes many arguments, which are needed to populate the infographic with information
    """

    def __init__(
        self,
        season: str,
        first_hc: list[int],
        date_of_first_hc: datetime,
        round_of_first_hc: int | None,
        permutations: int,
        result_detail: dict[int, dict[int, GameResult]],
        team_details: dict[int, Team],
        nteams: int,
        save_location: Path,
    ):
        self.season: str = season
        self.first_hc: list[int] = first_hc
        self.date_of_first_hc: datetime = date_of_first_hc
        self.round_of_first_hc: int | None = round_of_first_hc
        self.permutations: int = permutations
        self.team_details: dict[int, Team] = team_details
        self.nteams: int = nteams
        self.result_detail: dict[int, dict[int, GameResult]] = result_detail
        self.save_location: Path = save_location

    def _generate_points(self) -> None:
        """generates an equidistant set of x and y points which will be placements for each
        team in the circle"""
        logger.debug("Generating points for infographic")

        # generic parameters for the shape
        a: int = 10
        # b: int = 10 # (initially experimented with an ellipse, but stuck with a circle because easier for now)

        # generate evenly spaced angles between 0 and 2pi
        theta: np.ndarray = np.linspace(0, 2 * np.pi, self.nteams + 1)
        x_flat: np.ndarray = a * np.cos(theta)
        y_flat: np.ndarray = a * np.sin(theta)
        self.x: list[float] = x_flat.tolist()
        self.y: list[float] = y_flat.tolist()

    def create_infographic(self) -> None:
        """using matplotlib to build an annotated circle, with team logos as points"""

        # plot and setup
        _, ax = plt.subplots(figsize=(20, 20))
        ax.set_axis_off()  # this aint no graph
        ax.set_facecolor("#FFFDD0")  # slightly off-white

        # annoate date_achieved, and permutations in the circle of the infographic
        ax.annotate(
            f"{self.season}\n1st Hamiltonian Cycle Achieved in Rnd. {self.round_of_first_hc}\n{self.date_of_first_hc:%a %d %b %H:%M }\nPermys: {self.permutations:,}",
            xy=(0, 0),
            size=40,
            ha="center",
            va="center",
        )

        # plot the teams as points on the circle
        self._generate_points()
        ax.scatter(self.x, self.y)

        # matplotlib renders based on generated order, hence images first then annotations

        # images
        logger.debug("Drawing logos")
        for i, cur_winner in enumerate(self.first_hc):
            try:
                cur_loser: int = self.first_hc[i + 1]
            except IndexError:
                # if reached end of list, return first in list
                cur_loser: int = self.first_hc[0]

            img: np.ndarray = plt.imread(
                self.team_details[cur_winner].logo_file, format="png"
            )  # reminder - fix this png format read for other APIs (ie. allow other formats, pass in as argument)

            imagebox: OffsetImage = OffsetImage(
                img, zoom=0.8
            )  # reminder, make this an argument as other league logos will differ
            imagebox.image.axes = ax

            # 'annotate' the logo on the image
            ab: AnnotationBbox = AnnotationBbox(
                imagebox, (self.x[i], self.y[i]), bboxprops={"edgecolor": "none"}
            )
            ax.add_artist(ab)

        # annotations
        logger.debug("Applying annotations")
        for i, cur_winner in enumerate(self.first_hc):
            try:
                cur_loser: int = self.first_hc[i + 1]
            except IndexError:
                # if reached end of list, return first in list - expected and ineligantly handled...
                cur_loser: int = self.first_hc[0]
            cur_game_deets: GameResult = self.result_detail[cur_winner][cur_loser]
            cur_round: int = cur_game_deets.round
            cur_winner_score: int = cur_game_deets.winner_score
            cur_loser_score: int = cur_game_deets.loser_score

            # the cur_x and next_x indicate the to-from for each arrow
            cur_x: float = self.x[i]
            cur_y: float = self.y[i]
            try:
                next_x: float = self.x[i + 1]
                next_y: float = self.y[i + 1]
            except IndexError:
                # reached end of circle, so we want the last arrow to point to starting point
                next_x: float = self.x[0]
                next_y: float = self.y[0]
            # the 0.85 is to move the annotations slightly in, so they appear 'next' to the arrows
            mid_x: float = ((cur_x + next_x) / 2) * 0.85
            mid_y: float = ((cur_y + next_y) / 2) * 0.85

            # draw the arrow
            ax.annotate(
                "",
                xy=(next_x, next_y),
                xytext=(cur_x, cur_y),
                arrowprops=dict(
                    arrowstyle="-|>",
                    lw=10,
                    shrinkA=60,
                    shrinkB=60,
                    mutation_scale=40,
                ),
            )

            # draw the game result details
            ax.annotate(
                f"Rnd. {cur_round}\n{cur_winner_score}-{cur_loser_score}",
                xy=(mid_x, mid_y),
                size=20,
                ha="center",
                va="center",
            )

        # neaten the presentation
        ax.set_aspect("equal")

        # output resulting infograph to file
        if not self.save_location.parent.is_dir():
            self.save_location.parent.mkdir(parents=True, exist_ok=True)

        plt.savefig(
            self.save_location
            / Path(f"hamiltonian_cycle_infographic_{self.season}.png")
        )

        logger.debug(f"Infographic produced and saved to {self.save_location}")
