"""Main script runner"""
from types import SimpleNamespace
from datetime import datetime

import argparser
from csvreader import (
    CSVWrongValueException,
    FlightRowValidator,
    CSVHeaderException,
    FlightCSVReader,
    StartDateFilter,
    BagRowFilter,
)
from flighthandler import (
    FlightTripDataGenerator,
    DefaultLayoverRule,
    FlightGraph,
)


namespace = SimpleNamespace(
    destination="",
    reverse=False,
    start_date="",
    min_layover=1,
    max_layover=6,
    origin="",
    bags=0,
    csv="",
)


def main():
    """Main entry point"""
    # Create a csv reader to deal with flight data csv
    try:
        flight_csv_reader = FlightCSVReader(namespace.csv)
    except FileNotFoundError:
        print(f"error: {namespace.csv} file not found")
        exit(1)

    # Create row validator for reading csv file
    row_validator = FlightRowValidator()

    # Validate each csv row
    flight_csv_reader.add_row_validator(row_validator)

    # Create datetime object from string, comes from --start-date argument
    start_date = datetime.strptime(namespace.start_date, "%Y-%m-%d")

    # Add start date filter to check if there are some rows that can be dropped
    # If the --start-date argument is greater than the departure time of a
    # flight, we drop the row
    start_date_filter = StartDateFilter(start_date)
    flight_csv_reader.add_row_filter(start_date_filter)

    # Add bag filter, to check if we can ignore some csv rows.
    # If the --bags argument greater that the flights allowed size, we drop the 
    # row.
    bag_row_filter = BagRowFilter(namespace.bags)
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
    layover_rule = DefaultLayoverRule(namespace.min_layover,
                                      namespace.max_layover)

    # Add layover to the graph
    flight_graph.set_layover_rule(layover_rule)

    # It will contain the list of all calculated trips, e.g. from A to C:
    # [
    #   [Flight(origin=A, destination=B), Flight(origin=B, destination=C), ...],
    #   [Flight(origin=A, destination=C)],
    #   ...
    # ]
    trips = []

    # If --reverse argument is set to true, the reverse method is called
    if namespace.reverse:
        trips = flight_graph.find_trips_reverse(namespace.origin,
                                                namespace.destination,
                                                start_date)
    else:
        trips = flight_graph.find_trips(namespace.origin, namespace.destination,
                                        start_date)

    # Some plain object to handle the correct format of printing out the results
    data_generator = FlightTripDataGenerator(trips, namespace.origin,
                                             namespace.destination,
                                             namespace.bags)

    return data_generator.to_json()


if __name__ == "__main__":
    # Getting the arguments from the CLI
    arguments = argparser.get_args()

    # Populate the namespace object
    namespace.__dict__.update(arguments.__dict__)

    # Start the process and print out the results
    print(main())
