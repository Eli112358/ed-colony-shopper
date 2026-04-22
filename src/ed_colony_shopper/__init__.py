from datetime import timedelta
from logging import getLogger, basicConfig, INFO, Logger

import xerox

from ed_colony_shopper.needed import collect_needed_commodities, Commodity
from ed_colony_shopper.search import search_inara, Market


def init_logger() -> Logger:
    basicConfig(level=INFO, format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
    return getLogger("E:D Colony Shopper")


def main():
    logger = init_logger()
    logger.info("Starting ...")
    system, needed_commodities = collect_needed_commodities()
    needed_most: tuple[str, Commodity] = '', Commodity('', 0, 0, 0, 0)
    for commodity in needed_commodities:
        if needed_commodities[commodity].needed > needed_most[1].needed:
            needed_most = commodity, needed_commodities[commodity]
    markets: list[Market] = search_inara(system, needed_most[0], strict_star_dist=True)
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
    profit_margin = (100 * (needed_most[1].payment - target_market.price) / needed_most[1].payment)
    logger.info(f'Target market is "{target_market.station}" in the "{target_market.system}" system')
    logger.info(f"Profit margin: {profit_margin:.2f}%")
    logger.info(f"Need {needed_most[1].needed} more {needed_most[0]}")
    xerox.copy(target_market.system)
    logger.info("Target system name has been copied into clipboard")
