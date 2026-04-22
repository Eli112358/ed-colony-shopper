import json
from dataclasses import dataclass
from logging import getLogger, Logger
from pathlib import Path
from typing import Any


@dataclass
class Commodity:
    name: str
    required: int
    provided: int
    payment: int
    needed: int

    def __add__(self, other: Commodity) -> Commodity:
        if not other:
            return self
        payment: int = max(self.payment, other.payment)
        return Commodity(self.name, self.required, self.provided, payment, self.needed + other.needed)


def market_connector_data() -> Path:
    # todo: cross-platform
    return Path("~/.var/app/io.edcd.EDMarketConnector/data/EDMarketConnector").expanduser()

def colony_data() -> Path:
    # if EDMC inoperable or not installed:
        # todo: own storage
    return market_connector_data() / "colonization" / "constructions.json"


def parse_commodity(commodity_data: dict[str, str | int], quantities: bool = True) -> Commodity:
    name: str = str(commodity_data["commodity"])
    required: int = int(commodity_data["required"]) if quantities else 0
    provided: int = int(commodity_data["provided"]) if quantities else 0
    payment: int = int(commodity_data["payment"])
    needed: int = int(commodity_data["required"]) - int(commodity_data["provided"]) if quantities else 0
    return Commodity(name, required, provided, payment, needed)


def collect_required(constructions: list[dict[str, Any]]) -> list[dict[str, Commodity]]:
    return [{commodity_data["commodity"]: parse_commodity(commodity_data) for commodity_data in construction["required"].values()} for construction in constructions]


def collect_needed_commodities() -> tuple[str, dict[str, list[int]]]:
    """
    :return:
    A tuple of commodity name, a list of remaining and payment
    """
    logger: Logger = getLogger('needed_commodities')
    logger.info("Collecting needed commodities")
    # if EDMC inoperable or not installed:
        # todo: manual mode
        # todo: save results to own storage
    commodities: dict[str, list[int]] = {}
    constructions: list[dict[str, Any]] = json.load(open(colony_data()))
    system: str = ""
    for construction in constructions:
        construction: dict[str, Any]
        if not system:
            system = construction["system"]
        required: dict[str, dict[str, Any]] = construction["required"]
        for commodity in required:
            if commodity not in commodities:
                commodities[commodity] = [0, required[commodity]["payment"]]
            commodities[commodity][0] += required[commodity]["required"] - required[commodity]["provided"]
    return system, commodities
