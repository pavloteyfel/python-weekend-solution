"""Main script runner"""
from types import SimpleNamespace
from datetime import datetime
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
import argparser


# Namespace object used by unittests and argparser module 
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
    
    # Do we have the file?
    except FileNotFoundError:
        print(f"error: {namespace.csv} file not found")
        exit(1)

    # Create row validator for reading csv file
    row_validator = FlightRowValidator()
    flight_csv_reader.add_row_validator(row_validator)

    # Create datetime object, comes from --start-date argument
    start_date = datetime.strptime(namespace.start_date, "%Y-%m-%d")

    # Add start date filter to check if there are some rows that can be dropped
    # If the --start-date argument is greater than the departure time of a
    # flight, we drop the row
    start_date_filter = StartDateFilter(start_date)
    flight_csv_reader.add_row_filter(start_date_filter)

    # Add bag filter, to check if we can ignore some csv rows during loading
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
    
    # Are the headers ok?
    except CSVHeaderException as error:
        print(error)
        exit(1)
    
    # Are the values ok?
    except CSVWrongValueException as error:
        print(error)
        exit(1)

    # Before we start the calculation we feed some layover rules
    layover_rule = DefaultLayoverRule(namespace.min_layover,
                                      namespace.max_layover)
    flight_graph.set_layover_rule(layover_rule)

    # A list that will contain the list of all calculated trips, 
    # e.g. from A to C:
    # [
    #   [Flight(origin=A, destination=B), Flight(origin=B, destination=C), ...],
    #   [Flight(origin=A, destination=C)],
    #   ...
    # ]
    trips = []

    # If --reverse argument is present, the reverse method is called
    if namespace.reverse:
        trips = flight_graph.find_trips_reverse(namespace.origin,
                                                namespace.destination,
                                                start_date)
    # If not, then use the one way method
    else:
        trips = flight_graph.find_trips(namespace.origin, 
                                        namespace.destination,
                                        start_date)

    # Eventually the list is consumed by this class, that can conver object
    # data into json format
    data_generator = FlightTripDataGenerator(trips, 
                                             namespace.origin,
                                             namespace.destination,
                                             namespace.bags)

    # We arrived :)
    return data_generator.to_json()


if __name__ == "__main__":
    # Get the arguments from the CLI
    arguments = argparser.get_args()

    # Populate the namespace object
    namespace.__dict__.update(arguments.__dict__)

    # Start the process and print out the results into sdtout
    print(main())
