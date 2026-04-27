from datetime import timedelta
from logging import getLogger, basicConfig, INFO, Logger

import xerox

from ed_colony_shopper.needed import collect_needed_commodities, Commodity
from ed_colony_shopper.search import search_inara, Market


def init_logger() -> Logger:
    basicConfig(level=INFO, format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
    return getLogger("E:D Colony Shopper")


def get_system_and_commodity(logger: Logger) -> tuple[str, Commodity]:
    system, needed_commodities = collect_needed_commodities()
    sorted_commodities: list[Commodity] = list(needed_commodities.values())
    sorted_commodities.sort(key=lambda c: c.needed, reverse=True)
    logger.debug("Sorted commodities:")
    for commodity in sorted_commodities:
        logger.debug(f"Commodity: {commodity.name}, {commodity.needed}")
    commodity_needed_most: Commodity = sorted_commodities[0]
    return system, commodity_needed_most


def main():
    logger = init_logger()
    logger.info("Starting ...")
    system, commodity_needed_most = get_system_and_commodity(logger)
    markets: list[Market] = search_inara(system, commodity_needed_most.name, strict_star_dist=True)
    oldest_market = Market("", "", 0, 0.0, 0, 0, timedelta(0))
    cheapest_market = Market("", "", 0, 0.0, 0, 1_000_000_000, timedelta(0))
    for market in markets:
        if market.price < cheapest_market.price:
            cheapest_market = market
        if market.age > oldest_market.age:
            oldest_market = market
    target_market = cheapest_market
    if oldest_market.age > timedelta(days=7):
        target_market = oldest_market
    profit_margin = (100 * (commodity_needed_most.payment - target_market.price) / commodity_needed_most.payment)
    logger.info(f'Target market is "{target_market.station}" in the "{target_market.system}" system')
    logger.info(f"Profit margin: {profit_margin:.2f}%")
    logger.info(f"Need {commodity_needed_most.needed} more {commodity_needed_most.name}")
    xerox.copy(target_market.system)
    logger.info("Target system name has been copied into clipboard")
