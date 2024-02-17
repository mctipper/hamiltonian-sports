""" hacky config file, used python instead of pyyaml since there isn't much config here (currently)
"""


class Config:
    email: str = "dummy@email.com"  # update this with your email address
    valid_leagues_seasons: dict[str, list[str]] = {
        "afl": [str(yr) for yr in range(1897, 3000)],
        "nrl": [str(yr) for yr in range(1981, 3000)],
    }

    def valid_seasons(self, league: str) -> list[str]:
        return self.valid_leagues_seasons[league]
