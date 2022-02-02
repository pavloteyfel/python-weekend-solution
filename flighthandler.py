"""Module for organising flight related classes"""
from typing import Any, Generator, Optional, Protocol
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from json import dumps

from csvreader import DATE_TIME_PATTERN


@dataclass
class Flight:
    """Contaner for flight data row"""

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

    def get_full_price(self, bags_count: int) -> float:
        """Calculate the total price based on the bag number and base price"""
        return self.base_price + (bags_count * self.bag_price)

    def get_travel_time(self) -> timedelta:
        """Calculate the total travel time of a flight"""
        return self.get_arrival_time() - self.get_departure_time()

    def get_arrival_time(self) -> datetime:
        """Convert date time string to datetime object"""
        return datetime.strptime(self.arrival, DATE_TIME_PATTERN)

    def get_departure_time(self) -> datetime:
        """Convert date time string to datetime object"""
        return datetime.strptime(self.departure, DATE_TIME_PATTERN)


@dataclass
class FlightPath:
    """Container for all Flight objects that are necessary to get from A airport to B
    airport"""

    fligths: list[Flight]
    bags_allowed: int = field(init=False, default=0)
    bags_count: int
    destination: str
    origin: str
    total_price: float = field(init=False, default=0.0)
    travel_time: str = field(init=False, default="")

    def __post_init__(self):
        # Maybe creating @property for these would be a better option
        bags_allowed: int = 999
        total_price: float = 0.0
        travel_time: timedelta = timedelta()

        for flight in self.fligths:
            bags_allowed = min(bags_allowed, flight.bags_allowed)
            total_price += flight.get_full_price(self.bags_count)
            travel_time += flight.get_travel_time()

        self.bags_allowed = bags_allowed
        self.total_price = total_price
        self.travel_time = str(travel_time)

    # Used to calculate the final order flight paths
    def __gt__(self, other: "FlightPath"):
        return self.total_price > other.total_price

    # Used to calculate the final order flight paths
    def __lt__(self, other: "FlightPath"):
        return self.total_price < other.total_price


class LayoverRule(Protocol):
    """Protocol for defining min and max layorver rules"""

    def validate(self, prev_flight: Flight, next_flight: Flight) -> bool:
        """Compare two sequential flights to check if the meet the validation protocol"""
        ...


class DefaultLayoverRule:
    """Default layover logic implementation"""

    def __init__(self, min_layover: int, max_layover: int):
        self.min_layover = min_layover
        self.max_layover = max_layover

    def validate(self, prev_flight: Flight, next_flight: Flight) -> bool:
        """Comapre previous flight arrival time to the next flight's departure time"""
        min_hour_time = timedelta(hours=self.min_layover)
        max_hour_time = timedelta(hours=self.max_layover)
        difference = next_flight.get_departure_time() - prev_flight.get_arrival_time()
        return min_hour_time <= difference <= max_hour_time


class FlightGraph:
    """Store Flight objects in a dict based graph for quick path finding"""

    def __init__(self, flights: Generator[dict[str, Any], None, None]):
        self.graph: dict = {}
        self.layover_rule: Optional[LayoverRule] = None

        # Self populates during initialising the graph
        self.create_graph(flights)

    def create_graph(self, flights: Generator[dict[str, Any], None, None]):
        """Populate the graph with list of Flight objects for every airport
        {
            "WIW": [Flight(origin=WIW, destination=RFZ), Flight(...), Flight(...), ...],
            "RFZ": [Flight(...), Flight(...)],
            ...
        }
        """
        for flight_data in flights:
            flight_object = Flight(**flight_data)
            if flight_object.origin not in self.graph:
                self.graph[flight_object.origin] = []
            self.graph[flight_object.origin].append(flight_object)

    def set_layover_rule(self, rule: LayoverRule):
        """Add Layover to the FlightGraph"""
        self.layover_rule = rule

    def find_paths(
        self, origin: str, destination: str, start_date: datetime
    ) -> list[list[Flight]]:
        """Main method for finding all paths in the following way:
        [
            [Flight(), ...],
            [Flight(), Flight()],
            [Flight(), Flight(), Flight()],
            ...
        ]
        By path I mean list of Flight objects that are necessary to get from A airport to B
        """

        # The eventual list that will contain all the paths
        paths: list[list[Flight]] = []

        # Going through all the flights departing from origin, empty list for error handling reasons
        for flight in self.graph.get(origin, []):

            # This check will play a bigger role for reverse path finding.
            # All the past flights are dropped if start_date is specificed,
            # so if no reverse path if calculated this is a little bit reduntant checking.
            if start_date <= flight.get_departure_time():

                #  Keeping track of all visited airports, to avoid A->B->A->C loops
                visited_airport: set = set()

                # Just feeding the explore algorithm with mutable list to keeping track
                # of current paths
                current_path: list = []

                # The main method for finding all correct flights starting from the origin
                self.explore(flight, destination, visited_airport, current_path, paths)

        return paths

    def find_paths_reverse(
        self, origin: str, destination: str, start_date: datetime
    ) -> list[list[Flight]]:
        """Method for finding all reverse paths, based on the find_paths() method"""

        all_paths: list[list[Flight]] = []

        # We are doing this in two parts, first we get all flights from A to B
        paths = self.find_paths(origin, destination, start_date)

        # After that we iterate through these paths and extend them with all paths from B to A
        for path in paths:

            # Getting the last flight to the target airport
            last_flight = path[-1]

            # Getting the arrival to the target airport
            last_flight_arrival_time = last_flight.get_arrival_time()

            # Here we call again the find_paths method, switching the origin and destination,
            # and filter out based on the last flight's arrival time.
            # So we want see here all flights that starts from B airport and are after 
            # the arrival time.
            # No layover rule applied here.
            reverse_paths = self.find_paths(
                destination, origin, last_flight_arrival_time
            )

            # Extend our original list with reverse paths as well
            for reverse_path in reverse_paths:
                extended_paths = path.copy()
                extended_paths += reverse_path
                all_paths.append(extended_paths)

        return all_paths

    def explore(self, flight: Flight, destination: str, visited_airport: set, 
            current_path: list, paths: list[list[Flight]]):
        """Recursive Depth First Search method for finding valid paths"""
        is_correct_path = True
        visited_airport.add(flight.origin)
        visited_airport.add(flight.destination)
        current_path.append(flight)
        if flight.destination == destination:
            paths.append(current_path.copy())
        else:
            for next_flight in self.graph[flight.destination]:
                if (
                    next_flight.destination not in visited_airport
                    and self.is_valid_layover(flight, next_flight)
                ):
                    self.explore(
                        next_flight, destination, visited_airport, current_path, paths
                    )
            is_correct_path = False
        current_path.pop()
        if is_correct_path:
            visited_airport.remove(flight.destination)

    def is_valid_layover(self, prev_flight: Flight, next_flight: Flight) -> bool:
        """Method utilises the LayoverRule protocol to check to filter out non-valid layovers"""
        if self.layover_rule:
            return self.layover_rule.validate(prev_flight, next_flight)
        return True


class FlightPathDataGenerator:
    """Converts path information into presentable format"""

    def __init__(self, paths: list[list[Flight]], origin: str, destination: str, bags: int):
        self.paths: list = []
        self.origin: str = origin
        self.destination: str = destination
        self.bags: int = bags
        self.add_paths(paths)

    def add_paths(self, paths: list[list[Flight]]):
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

    def to_dict(self) -> list[dict[str, Any]]:
        """Returns the flight data objects to list of dicts"""
        return [asdict(path) for path in self.paths]

    def to_json(self) -> str:
        """Returns formatted json string from list of dictionaries"""
        return dumps(self.to_dict(), indent=4)
