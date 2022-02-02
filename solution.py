from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from json import dumps

import argparser
from csvreader import (
    DATE_TIME_PATTERN,
    BagRowFilter,
    CSVHeaderException,
    CSVWrongValueException,
    FlighCSVReader,
    FlightRowValidator,
    StartDateFilter,
)

# Parameters
MIN_LAYOVER = 1
MAX_LAYOVER = 6
CSV = ""
FROM = ""
TO = ""
BAGS = 0
REVERSE = False
START_DATE = ""


@dataclass
class Flight:
    flight_no: str
    origin: str
    destination: str
    departure: str
    arrival: str
    base_price: float
    bag_price: float
    bags_allowed: int

    def __post_init__(self):
        self.base_price = float(self.base_price)
        self.bag_price = int(self.bag_price)
        self.bags_allowed = int(self.bags_allowed)

    def __hash__(self):
        return id(self)

    def get_full_price(self, bags_count):
        return self.base_price + (bags_count * self.bag_price)

    def get_travel_time(self):
        return self.get_arrival_time() - self.get_departure_time()

    def get_arrival_time(self):
        return datetime.strptime(self.arrival, DATE_TIME_PATTERN)

    def get_departure_time(self):
        return datetime.strptime(self.departure, DATE_TIME_PATTERN)


@dataclass
class FlightPath:
    fligths: list[Flight]
    bags_allowed: int = field(init=False, default=0)
    bags_count: int
    destination: str
    origin: str
    total_price: float = field(init=False, default=0.0)
    travel_time: str = field(init=False, default="")

    def __post_init__(self):
        bags_allowed = float("inf")
        total_price = 0.0
        travel_time = timedelta()

        for flight in self.fligths:
            bags_allowed = min(bags_allowed, flight.bags_allowed)
            total_price += flight.get_full_price(self.bags_count)
            travel_time += flight.get_travel_time()

        self.bags_allowed = bags_allowed
        self.total_price = total_price
        self.travel_time = str(travel_time)

    def __gt__(self, other):
        return self.total_price > other.total_price

    def __lt__(self, other):
        return self.total_price < other.total_price


class LayoverRule:
    def __init__(self, min_layover, max_layover):
        self.min_layover = min_layover
        self.max_layover = max_layover

    def validate(self, prev_flight, next_flight):
        min_hour_time = timedelta(hours=self.min_layover)
        max_hour_time = timedelta(hours=self.max_layover)
        difference = next_flight.get_departure_time() - prev_flight.get_arrival_time()
        return min_hour_time <= difference <= max_hour_time


class FlightGraph:
    def __init__(self, flights):
        self.graph = {}
        self._create_graph(flights)
        self._layover_rule = None

    def _create_graph(self, flights):
        for flight_data in flights:
            flight_object = Flight(**flight_data)
            if flight_object.origin not in self.graph:
                self.graph[flight_object.origin] = []
            self.graph[flight_object.origin].append(flight_object)

    def set_layover_rule(self, rule):
        self._layover_rule = rule

    def find_paths(self, origin, destination, start_date):
        paths = []
        for flight in self.graph.get(origin, []):
            if start_date <= flight.get_departure_time():
                visited_city = set()
                current_path = []
                self._explore(flight, destination, visited_city, current_path, paths)
        return paths

    def find_paths_reverse(self, origin, destination, start_date):
        all_paths = []
        paths = self.find_paths(origin, destination, start_date)

        for path in paths:

            last_flight = path[-1]
            last_flight_arrival_time = last_flight.get_arrival_time()
            reverse_paths = self.find_paths(
                destination, origin, last_flight_arrival_time
            )

            for reverse_path in reverse_paths:
                extended_paths = path.copy()
                extended_paths += reverse_path
                all_paths.append(extended_paths)

        return all_paths

    def _explore(self, flight, destination, visited_city, current_path, paths):
        is_correct_path = True
        visited_city.add(flight.origin)
        visited_city.add(flight.destination)
        current_path.append(flight)
        if flight.destination == destination:
            paths.append(current_path.copy())
        else:
            for next_flight in self.graph[flight.destination]:
                if next_flight.destination not in visited_city and self._valid_layover(
                    flight, next_flight
                ):
                    self._explore(
                        next_flight, destination, visited_city, current_path, paths
                    )
            is_correct_path = False
        current_path.pop()
        if is_correct_path:
            visited_city.remove(flight.destination)

    def _valid_layover(self, prev, next):
        if self._layover_rule:
            return self._layover_rule.validate(prev, next)
        return True


class FlightPathDataGenerator:
    """Converts path information into presentable format"""

    def __init__(self, paths, origin, destination, bags):
        self.paths = []
        self.origin = origin
        self.destination = destination
        self.bags = bags
        self.add_paths(paths)

    def add_paths(self, paths):
        """Converts list of Flight objects into FlightPath objects where the Flight
        objects are ordered based on the total price data"""
        for flights in paths:
            self.paths.append(
                FlightPath(
                    fligths=flights,
                    origin=self.origin,
                    destination=self.destination,
                    bags_count=self.bags,
                )
            )
        self.paths.sort()

    def to_dict(self):
        """Returns the flight data objects to list of dicts"""
        return [asdict(path) for path in self.paths]

    def to_json(self):
        """Returns formatted json string from list of dictionaries"""
        return dumps(self.to_dict(), indent=4)


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

    layover_rule = LayoverRule(MIN_LAYOVER, MAX_LAYOVER)

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
