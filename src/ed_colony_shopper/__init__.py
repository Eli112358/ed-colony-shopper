from datetime import timedelta
from logging import getLogger, basicConfig, INFO

from ed_colony_shopper.needed import collect_needed_commodities
from ed_colony_shopper.search import search_inara, Market


def main():
    logger = getLogger("ed_colony_shopper")
    basicConfig(level=INFO, format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
    logger.info("Starting ed_colony_shopper ...")
    system, needed_commodities = collect_needed_commodities()
    needed_most: tuple[str, int] = '', 0
    for commodity in needed_commodities:
        if needed_commodities[commodity][0] > needed_most[1]:
            needed_most = commodity, needed_commodities[commodity][0]
    markets: list[Market] = search_inara(system, needed_most[0], strict_star_dist=True)
    oldest_market = Market("", "", 0, 0.0, 0, 0, timedelta(0))
    cheapest_market = Market("", "", 0, 0.0, 0, 1_000_000_000, timedelta(0))
    for market in markets:
        if market.price < cheapest_market.price:
            cheapest_market = market
        if market.age > oldest_market.age:
            oldest_market = market
    logger.info(f"Oldest market: {oldest_market}")
    logger.info(f"Cheapest market: {cheapest_market}")

