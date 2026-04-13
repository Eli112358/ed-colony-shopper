from logging import getLogger, basicConfig, INFO

from ed_colony_shopper.needed import collect_needed_commodities


def main():
    logger = getLogger("ed_colony_shopper")
    basicConfig(level=INFO, format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
    # logger.setLevel(logging.INFO)
    logger.info("Starting ed_colony_shopper ...")
    system, needed_commodities = collect_needed_commodities()
