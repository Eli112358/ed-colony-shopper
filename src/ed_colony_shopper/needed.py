import json
from dataclasses import dataclass
from functools import reduce
from logging import getLogger, Logger
from pathlib import Path
from typing import Any

from ed_colony_shopper.inara import MAPPING


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


def reduce_commodities(required_commodities: list[dict[str, Commodity]]) -> dict[str, Commodity]:
    initial_commodities: dict[str, Commodity] = {commodity_name: Commodity(commodity_name, 0, 0, 0, 0) for commodity_name in MAPPING}
    needed_commodities: dict[str, Commodity] = reduce(lambda x, y: {k: x[k] + y.get(k) for k in x}, required_commodities, initial_commodities)
    commodities: list[Commodity] = list(filter(lambda commodity: commodity.needed > 0, needed_commodities.values()))
    needed_commodities: dict[str, Commodity] = {c.name: c for c in commodities}
    return needed_commodities


def collect_needed_commodities() -> tuple[str, dict[str, Commodity]]:
    logger: Logger = getLogger('Commodities')
    logger.info("Collecting needed commodities")
    # if EDMC inoperable or not installed:
        # todo: manual mode
        # todo: save results to own storage
    constructions: list[dict[str, Any]] = json.load(open(colony_data()))
    system: str = constructions[0]["system"]
    required_commodities: list[dict[str, Commodity]] = collect_required(constructions)
    needed_commodities: dict[str, Commodity] = reduce_commodities(required_commodities)
    return system, needed_commodities
