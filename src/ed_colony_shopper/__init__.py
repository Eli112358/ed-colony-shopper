from datetime import timedelta, datetime
from functools import cache
from importlib.metadata import version
from logging import getLogger, basicConfig, INFO, Logger

import xerox

from ed_colony_shopper.needed import collect_needed_commodities, Commodity
from ed_colony_shopper.search import search_inara, Market

PROJECT_NAME: str = "ed_colony_shopper"
SERVER_MAINTENANCE_WEEKDAY: int = 3 # Thursday


@cache
def get_days_since_weekly_maintenance() -> int:
    current_weekday = datetime.now().weekday()
    return (7 + current_weekday - SERVER_MAINTENANCE_WEEKDAY) % 7


def get_age_message(age: timedelta) -> tuple[int | str, str]:
    if age.days > 0:
        return age.days, "days"
    if age.seconds < 1:
        return "now", ""
    minutes: int = age.seconds // 60
    if minutes < 1:
        return age.seconds, "seconds"
    hours: int = minutes // 60
    if hours > 0:
        return hours, "hours"
    return minutes, "minutes"


def init_logger() -> Logger:
    basicConfig(level=INFO, format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
    return getLogger("E:D Colony Shopper")


def get_system_and_commodity() -> tuple[str, Commodity]:
    system, needed_commodities = collect_needed_commodities()
    sorted_commodities: list[Commodity] = list(needed_commodities.values())
    sorted_commodities.sort(key=lambda c: c.needed, reverse=True)
    commodity_needed_most: Commodity = sorted_commodities[0]
    return system, commodity_needed_most


def get_cheapest_and_oldest(commodity_needed_most: Commodity, system: str) -> tuple[Market, Market]:
    markets: list[Market] = search_inara(system, commodity_needed_most.name, strict_star_dist=True)
    if len(markets) == 0:
        markets = search_inara(system, commodity_needed_most.name, include_surface=True, strict_star_dist=True)
    markets.sort(key=lambda m: m.age, reverse=True)
    oldest_market: Market = markets[0]
    markets.sort(key=lambda m: m.price)
    cheapest_market: Market = markets[0]
    return cheapest_market, oldest_market


def get_commodity_and_market() -> tuple[Commodity, Market]:
    system, commodity_needed_most = get_system_and_commodity()
    cheapest_market, oldest_market = get_cheapest_and_oldest(commodity_needed_most, system)
    use_oldest: bool = oldest_market.age.days > get_days_since_weekly_maintenance()
    return commodity_needed_most, oldest_market if use_oldest else cheapest_market


def main():
    logger = init_logger()
    version_str: str = version(PROJECT_NAME)
    logger.info(f"Starting v{version_str} ...")
    logger.info(f"It has been {get_days_since_weekly_maintenance()} days since weekly server maintenance")
    commodity, market = get_commodity_and_market()
    profit_margin = (100 * (commodity.payment - market.price) / commodity.payment)
    logger.info(f'Target market is "{market.station}" in the "{market.system}" system')
    logger.info(f"Profit margin: {profit_margin:.2f}%")
    logger.info(f"Need {commodity.needed} more {commodity.name}")
    logger.info("Data age: {} {}".format(*get_age_message(market.age)))
    xerox.copy(market.system)
    logger.info("Target system name has been copied into clipboard")
