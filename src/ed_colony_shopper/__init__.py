from logging import getLogger, basicConfig, INFO


def main():
    logger = getLogger("ed_colony_shopper")
    basicConfig(level=INFO, format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
    # logger.setLevel(logging.INFO)
    logger.info("Starting ed_colony_shopper ...")
