# todo: get from configurable Google Sheet (by DaftMav)
import logging
from dataclasses import dataclass
from datetime import timedelta

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.common.by import By

from ed_colony_shopper.inara import MAPPING, URL

MAX_STAR_DISTANCE: int = 30
MAX_STATION_DISTANCE: int = 2000
MIN_SUPPLY: int = 1000

# todo: make configurable/optional
MAX_PRICE_AGE: int = 7 * 24 # in hours


@dataclass
class Market:
    station: str
    system: str
    station_distance: int
    system_distance: float
    supply: int
    price: int
    age: timedelta

def parse_age(time_str: str) -> timedelta:
    days, hours, minutes = 0, 0, 0
    parts: list[str] = time_str.split(" ")
    if parts[1].startswith("day"):
        days = int(parts[0])
    elif parts[1].startswith("hour"):
        hours = int(parts[0])
    elif parts[1].startswith("minute"):
        minutes = int(parts[0])
    age: timedelta = timedelta(days=days, hours=hours, minutes=minutes)
    return age

def search_inara(system: str, commodity: str, restrict_age: bool = False, strict_star_dist: bool = False) -> list[Market]:
    logger = logging.getLogger("Inara")
    commodity_id: int = MAPPING[commodity]
    inara_url = URL.format(
        commodity_id=commodity_id,
        max_star_dist=MAX_STAR_DISTANCE,
        max_station_dist=MAX_STATION_DISTANCE,
        min_supply=MIN_SUPPLY,
        max_age=MAX_PRICE_AGE if restrict_age else 0,
        system=system.replace(" ", "+"),
    )
    logger.info(f"Inara URL: {inara_url}")
    logger.info(f"Searching Inara for {commodity} near {system}...")
    options = Options()
    options.add_argument("headless")
    driver = webdriver.Chrome(options=options)
    driver.get(inara_url)
    data_rows = driver.find_elements(By.CSS_SELECTOR, "#DataTables_Table_0_wrapper tbody tr")
    cell_data: list[list[str]] = [[cell.text for cell in row.find_elements(By.CSS_SELECTOR, "td")] for row in data_rows]
    driver.quit()
    results = []
    for row in cell_data:
        supply = row[4].split("\n")
        supply.reverse()
        entry = Market(
            station=row[0].split(" | ")[0],
            system=row[0].split(" | ")[1].split("\ue81d︎")[0],
            station_distance=int(row[2].split(" ")[0].replace(",", "")),
            system_distance=float(row[3].split(" ")[0]),
            supply=int(supply[0].replace(",", "")),
            price=int(row[5].split(" ")[0].replace(",", "")),
            age=parse_age(row[6]),
        )
        if not strict_star_dist or entry.system_distance <= MAX_STAR_DISTANCE:
            results.append(entry)
    return results
