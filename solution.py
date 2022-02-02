from datetime import datetime

import argparser
from csvreader import (
    BagRowFilter,
    CSVHeaderException,
    CSVWrongValueException,
    FlighCSVReader,
    FlightRowValidator,
    StartDateFilter,
)
from flighthandler import DefaultLayoverRule, FlightGraph, FlightPathDataGenerator

# Parameters
MIN_LAYOVER = 1
MAX_LAYOVER = 6
CSV = ""
FROM = ""
TO = ""
BAGS = 0
REVERSE = False
START_DATE = ""


def main():

    try:
        flight_csv_reader = FlighCSVReader(CSV)
    except FileNotFoundError:
        print(f"error: {CSV} file not found")
        exit(1)

    start_date = datetime(1900, 1, 1)

    flight_csv_reader.add_row_validator(FlightRowValidator())

    if START_DATE:
        start_date = datetime.strptime(START_DATE, "%Y-%m-%d")
        start_date_filter = StartDateFilter(start_date)
        flight_csv_reader.add_row_filter(start_date_filter)

    if BAGS >= 0:
        bag_row_filter = BagRowFilter(BAGS)
        flight_csv_reader.add_row_filter(bag_row_filter)

    flights = flight_csv_reader.read()

    try:
        flight_graph = FlightGraph(flights)
    except CSVHeaderException as error:
        print(error)
        exit(1)
    except CSVWrongValueException as error:
        print(error)
        exit(1)

    layover_rule = DefaultLayoverRule(MIN_LAYOVER, MAX_LAYOVER)

    flight_graph.set_layover_rule(layover_rule)

    paths = []

    if REVERSE:
        paths = flight_graph.find_paths_reverse(FROM, TO, start_date)
    else:
        paths = flight_graph.find_paths(FROM, TO, start_date)

    data_generator = FlightPathDataGenerator(paths, FROM, TO, BAGS)

    return data_generator.to_json()


if __name__ == "__main__":
    arguments = argparser.get_args()
    MIN_LAYOVER = arguments.min_layover
    MAX_LAYOVER = arguments.max_layover
    CSV = arguments.csv
    FROM = arguments.origin
    TO = arguments.destination
    BAGS = arguments.bags
    REVERSE = arguments.reverse
    START_DATE = arguments.start
    result_json = main()
    print(result_json)
