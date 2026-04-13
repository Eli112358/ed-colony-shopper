import json
from logging import getLogger, Logger
from pathlib import Path
from typing import Any


def market_connector_data() -> Path:
    # todo: cross-platform
    return Path("~/.var/app/io.edcd.EDMarketConnector/data/EDMarketConnector").expanduser()

def colony_data() -> Path:
    # if EDMC inoperable not installed:
        # todo: own storage
    return market_connector_data() / "colonization" / "constructions.json"


def collect_needed_commodities() -> tuple[str, dict[str, list[int]]]:
    logger: Logger = getLogger('needed_commodities')
    logger.info("Collecting needed commodities")
    # if EDMC inoperable or not installed:
        # todo: manual mode
        # todo: save results to own storage
    commodities: dict[str, list[int]] = {}
    constructions: dict[str, Any] = json.load(open(colony_data()))
    system: str = ""
    for construction in constructions:
        construction: dict[str, Any]
        if not system:
            system = construction["system"]
        construction: dict[str, Any]
        required: dict[str, dict[str, Any]] = construction["required"]
        for commodity in required:
            if commodity not in commodities:
                commodities[commodity] = [0, required[commodity]["payment"]]
            commodities[commodity][0] += required[commodity]["required"] - required[commodity]["provided"]
    return system, commodities
