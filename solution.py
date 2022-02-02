from datetime import datetime

import argparser
from csvreader import (
    BagRowFilter,
    CSVHeaderException,
    CSVWrongValueException,
    FlightCSVReader,
    FlightRowValidator,
    StartDateFilter,
)
from flighthandler import DefaultLayoverRule, FlightGraph, FlightTripDataGenerator

# ------------------------------------------------------------------------------------- #
# Global parameters
# ------------------------------------------------------------------------------------- #

CSV = ""
ORIGIN = ""
DESTINATION = ""
REVERSE = False
START_DATE = ""
MIN_LAYOVER = 1
MAX_LAYOVER = 6


def main():
    # Creating a csv reader to deal with flight data csv
    try:
        flight_csv_reader = FlightCSVReader(CSV)
    except FileNotFoundError:
        print(f"error: {CSV} file not found")
        exit(1)

    # We will validate each csv row
    flight_csv_reader.add_row_validator(FlightRowValidator())

    # Create datetime object from string, comes from --start-date argument
    start_date = datetime.strptime(START_DATE, "%Y-%m-%d")

    # Add start date filter to check if we can drop some unnecessary csv rows.
    # If the --start-date argument are greater than the departure time of a flight,
    # we drop the row.
    start_date_filter = StartDateFilter(start_date)
    flight_csv_reader.add_row_filter(start_date_filter)

    # Add bag filter, to check if we can ignore some csv rows.
    # If the --bags argument greater that the flights allowed size, we drop the row.
    bag_row_filter = BagRowFilter(BAGS)
    flight_csv_reader.add_row_filter(bag_row_filter)

    # Getting a generator object from csv reader
    flights = flight_csv_reader.read()

    # Passing the generator object to create a flight hashmap for quick access
    # and calculations 
    try:
        flight_graph = FlightGraph(flights)
    except CSVHeaderException as error:
        print(error)
        exit(1)
    except CSVWrongValueException as error:
        print(error)
        exit(1)

    # Before we start the calculation we feed some layover rules
    layover_rule = DefaultLayoverRule(MIN_LAYOVER, MAX_LAYOVER)
    flight_graph.set_layover_rule(layover_rule)

    # It will contain the list of all calculated trips
    # By trip I mean list of flight objects: list[Flight(), Flight(), ...] that 
    # necessary to get you from A airport to B airport
    # By trips I mean a list of list of flights: list[list[Flight(), Flight(), ...]]
    # that are all the trips you can take
    trips = []

    # If --reverse argument set to true, we check all flight back to origin
    if REVERSE:
        trips = flight_graph.find_trips_reverse(ORIGIN, DESTINATION, start_date)
    else:
        trips = flight_graph.find_trips(ORIGIN, DESTINATION, start_date)

    # Some plain object to handle the correct format of printing out the resutls
    data_generator = FlightTripDataGenerator(trips, ORIGIN, DESTINATION, BAGS)

    return data_generator.to_json()


if __name__ == "__main__":
    # Getting the arguments from the CLI
    arguments = argparser.get_args()

    # Feeding them to the globals
    MIN_LAYOVER = arguments.min_layover
    MAX_LAYOVER = arguments.max_layover
    CSV = arguments.csv
    ORIGIN = arguments.origin
    DESTINATION = arguments.destination
    BAGS = arguments.bags
    REVERSE = arguments.reverse
    START_DATE = arguments.start_date

    # Start the process and print out the results
    print(main())
