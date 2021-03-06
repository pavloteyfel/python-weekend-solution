"""Module for organising flight related classes"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from json import dumps
from typing import Any, Generator, Optional, Protocol

from csvreader import DATE_TIME_PATTERN


@dataclass
class Flight:
    """Container for flight data CSV rows"""

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
class FlightTrip:
    """Container for all Flight objects that are necessary to get from A
    airport to B airport"""

    flights: list[Flight]
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

        for flight in self.flights:
            bags_allowed = min(bags_allowed, flight.bags_allowed)
            total_price += flight.get_full_price(self.bags_count)

        self.bags_allowed = bags_allowed
        self.total_price = total_price
        self.travel_time = self.get_travel_time()

    def get_travel_time(self):
        """Calculates the whole trave time"""
        start = self.flights[0]
        end = self.flights[-1]

        return str(end.get_arrival_time() - start.get_departure_time())

    # Used to calculate the final order flight trips
    def __gt__(self, other: "FlightTrip"):
        return self.total_price > other.total_price

    # Used to calculate the final order flight trips
    def __lt__(self, other: "FlightTrip"):
        return self.total_price < other.total_price


class LayoverRule(Protocol):
    """Protocol for defining min and max layover rules"""

    def validate(self, prev_flight: Flight, next_flight: Flight) -> bool:
        """Compare two sequential flights to check if the meet the validation
        protocol"""

        ...


class DefaultLayoverRule:
    """Default layover logic implementation"""

    def __init__(self, min_layover: int, max_layover: int):
        self.min_layover = min_layover
        self.max_layover = max_layover

    def validate(self, prev_flight: Flight, next_flight: Flight) -> bool:
        """Compare the previous flight arrival time to the next flight's
        departure time"""

        min_hour_time = timedelta(hours=self.min_layover)
        max_hour_time = timedelta(hours=self.max_layover)
        diff = next_flight.get_departure_time() - prev_flight.get_arrival_time()
        return min_hour_time <= diff <= max_hour_time


class FlightGraph:
    """Store Flight objects in a dict based graph for quick trip finding"""

    def __init__(self, flights: Generator[dict[str, Any], None, None]):
        self.graph: dict[str, list[Flight]] = {}
        self.layover_rule: Optional[LayoverRule] = None
        self.create_graph(flights)

    def create_graph(self, flights: Generator[dict[str, Any], None, None]):
        """Populate the graph with list of Flight objects for every airport
        {
            "WIW": [Flight(origin=WIW, destination=RFZ), Flight(...), ...],
            "RFZ": [Flight(...), Flight(...)],
            ...
        }
        """

        # Maybe a defaultdict would be a better idea
        for flight_data in flights:
            flight_object = Flight(**flight_data)
            if flight_object.origin not in self.graph:
                self.graph[flight_object.origin] = []
            self.graph[flight_object.origin].append(flight_object)

    def set_layover_rule(self, rule: LayoverRule):
        """Add Layover to the FlightGraph"""

        self.layover_rule = rule

    def find_trips(
        self, origin: str, destination: str, start_date: datetime
    ) -> list[list[Flight]]:
        """Main method for finding all trips"""

        # The eventual list that will contain all the trips (list of flights)
        trips: list[list[Flight]] = []

        # Going through all the flights departing from the origin airport
        for flight in self.graph.get(origin, []):
            # This might be a little bit redundant checking. But will be
            # useful for reverse trip calculation.
            if start_date <= flight.get_departure_time():
                # Keeping track of all visited airports, to avoid A->B->A->C
                # loops
                visited_airport: set[str] = set()

                # Provide a mutable list to the explore algorithm to
                # keeping track of current trips
                current_trip: list[Flight] = []

                # The main method for finding all correct flights starting
                # from the origin airport
                self.explore(flight, destination, visited_airport, current_trip, trips)

        return trips

    def find_trips_reverse(
        self, origin: str, destination: str, start_date: datetime
    ) -> list[list[Flight]]:
        """Method for finding all reverse trips, based on the find_trips()
        method"""

        # Will be an extended list of flight list with reverse trips
        all_trips: list[list[Flight]] = []

        # We are doing this in two parts, first we get all flights from A to B
        trips = self.find_trips(origin, destination, start_date)

        # After that we iterate through these trips and extend them with all
        # trips from B to A
        for trip in trips:

            # Getting the last flight to the target airport
            last_flight = trip[-1]

            # Getting the arrival to the target airport
            last_flight_arrival_time = last_flight.get_arrival_time()

            # Here we again call the find_trips method, switching the origin
            # and destination, and filtering out based on the last flight's
            # arrival time. So we want see here all flights that starts from
            # B airport and are after the arrival time. No layover rule
            # applied here.
            reverse_trips = self.find_trips(
                destination, origin, last_flight_arrival_time
            )

            # Extend our original list with reverse trips as well
            for reverse_trip in reverse_trips:
                extended_trips = trip.copy()
                extended_trips += reverse_trip
                all_trips.append(extended_trips)

        return all_trips

    def explore(
        self,
        flight: Flight,
        destination: str,
        visited_airport: set[str],
        current_trip: list[Flight],
        trips: list[list[Flight]],
    ):
        """Recursive Depth First Search method for finding valid trips"""

        # Keeping track of visited airports
        visited_airport.add(flight.origin)
        visited_airport.add(flight.destination)

        # Building our trip, adding the first flight to it
        current_trip.append(flight)

        # Check if we reached our destination
        if flight.destination == destination:
            # Let's add the current trip's copy to the list of all valid trips
            # Maybe creating a tuple would be more appropriate
            trips.append(current_trip.copy())

        # Still not there
        else:
            # Let's check what are the available flight option on the
            # destination's airport
            for next_flight in self.graph[flight.destination]:
                # We need a flight that flies to new airport we haven't been
                # before, and the layover are correct, min 1 hour and 6 hours
                # as default.
                if (
                    next_flight.destination not in visited_airport
                    and self.is_valid_layover(flight, next_flight)
                ):
                    # Let's go deep recursively
                    self.explore(
                        next_flight, destination, visited_airport, current_trip, trips
                    )

        # Let's explore the other flights from the previous airport, if there
        # any
        current_trip.pop()

        # We can visit this airport again maybe in different time
        visited_airport.remove(flight.destination)

    def is_valid_layover(self, prev_flight: Flight, next_flight: Flight) -> bool:
        """Method utilises the LayoverRule protocol to check to filter out
        non-valid layovers"""

        if self.layover_rule:
            return self.layover_rule.validate(prev_flight, next_flight)
        return True


class FlightTripDataGenerator:
    """Converts trip information into presentable format"""

    def __init__(
        self, trips: list[list[Flight]], origin: str, destination: str, bags: int
    ):
        self.trips: list[FlightTrip] = []
        self.origin: str = origin
        self.destination: str = destination
        self.bags: int = bags
        self.add_trips(trips)

    def add_trips(self, trips: list[list[Flight]]):
        """Converts a list of Flight objects into FlightTrip objects where the
        Flight objects are ordered based on the total price data"""

        for flights in trips:
            self.trips.append(
                FlightTrip(
                    flights=flights,
                    origin=self.origin,
                    destination=self.destination,
                    bags_count=self.bags,
                )
            )
        self.trips.sort()

    def to_dict(self) -> list[dict[str, Any]]:
        """Returns the flight data objects to list of dicts"""

        return [asdict(trip) for trip in self.trips]

    def to_json(self) -> str:
        """Returns a formatted json string from list of dictionaries"""

        return dumps(self.to_dict(), indent=4)
