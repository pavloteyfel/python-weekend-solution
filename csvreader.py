"""CSV module for reading flight data"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Generator, Optional, Protocol

DATE_TIME_PATTERN: str = "%Y-%m-%dT%H:%M:%S"
DATE_PATTERN: str = "%Y-%m-%d"
CSV_FIELDS: list[str] = [
    "flight_no",
    "origin",
    "destination",
    "departure",
    "arrival",
    "base_price",
    "bag_price",
    "bags_allowed",
]


class CSVRowFilter(Protocol):
    """Filter protocol for FlightCSVReader"""

    def filter_row(self, row: dict[str, str]) -> bool:
        """Check if the given row meets the conditions"""
        ...


class CSVRowValidator(Protocol):
    """Validator protocol for FlightCSVReader"""

    def validate_row(self, line: int, row: dict[str, str]):
        """Check if the given row contains correct data"""
        ...


class CSVHeaderException(Exception):
    """Custom exception for FlightCSVReader header checking"""

    ...


class CSVWrongValueException(Exception):
    """Custom exception for  CSVRowValidator row cell value checking"""

    ...


class CSVValidationException(Exception):
    """Custom exception for CSVRowValidator validation errors"""

    ...


class FlightCSVReader:
    """Custom CSV reader for flight related data"""

    def __init__(self, path: str):
        if not Path(path).exists():
            raise FileNotFoundError
        self.path: Path = Path(path)
        self.row_filters: list[CSVRowFilter] = []
        self.row_validator: Optional[CSVRowValidator] = None

    def add_row_filter(self, row_filter: CSVRowFilter):
        """Add CSVRowFilter to the reader"""

        self.row_filters.append(row_filter)

    def add_row_validator(self, row_validator: CSVRowValidator):
        """Add CSVRowValidator to the reader"""

        self.row_validator = row_validator

    def filter_row(self, row: dict[str, str]) -> bool:
        """Filter a particular row with CSVRowFilter"""

        valid = True
        for row_filter in self.row_filters:
            valid &= row_filter.filter_row(row)
        return valid

    def validate_row(self, row_line: int, row: dict[str, str]):
        """Validate a particular row with CSVRowValidator"""

        if self.row_validator:
            self.row_validator.validate_row(row_line, row)

    def read(self) -> Generator[dict[str, Any], None, None]:
        """Get row dict from the CSV file and apply CSVRowFilter and
        CSVRowValidator"""

        with open(self.path, newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)

            # Check if the headers are OK
            if reader.fieldnames != CSV_FIELDS:
                headers = ", ".join(CSV_FIELDS)
                message = f"error: Incorrect CSV headers. The following headers\
                    are expected: {headers}"
                raise CSVHeaderException(message)

            # Apply validation and filters
            for row in reader:
                self.validate_row(reader.line_num, row)
                if self.filter_row(row):
                    yield row


class BagRowFilter:
    """CSVRowFilter for filtering bag data in a CSV file"""

    def __init__(self, bags: int):
        self.bags = bags

    def filter_row(self, row: dict[str, str]) -> bool:
        """Filter out CSV rows where flight's allowed bag size >= bags"""

        return int(row["bags_allowed"]) >= self.bags


class StartDateFilter:
    """CSVRowFilter for filtering departure date in CSV file"""

    def __init__(self, start_date: datetime):
        self.start_date = start_date

    def filter_row(self, row: dict[str, str]) -> bool:
        """Filter out CSV rows where flight's departure time >= start date"""
        departure_time = datetime.strptime(row["departure"], DATE_TIME_PATTERN)
        return departure_time >= self.start_date


class FlightRowValidator:
    """CSVRowValidator for checking the data correctness of the CSV file"""

    def __init__(self):
        self.checkers: list[Callable[[tuple[str, Any]], None]] = [
            check_string,
            check_string,
            check_string,
            check_date,
            check_date,
            check_float,
            check_float,
            check_number,
        ]

    def validate_row(self, line: int, row: dict[str, str]):
        """Validate given row based on the sequence of prepared validation
        functions"""

        # Go through every cell and apply the corresponding checker method to it
        for checker, items in zip(self.checkers, row.items()):
            try:
                checker(items)
            except CSVValidationException as error:
                message = f"error: Wrong value in CSV file at row [{line}]: {error}"
                raise CSVWrongValueException(message) from error


def check_string(items: tuple[str, Any]):
    """Check if row cell is not empty"""

    key, value = items
    if not value:
        raise CSVValidationException(f"{key} cannot be an empty string.")


def check_date(items: tuple[str, Any]):
    """Check if row cell is in correct date time format"""

    key, value = items
    try:
        datetime.strptime(value, DATE_TIME_PATTERN)
    except ValueError as error:
        raise CSVValidationException(
            f"{key} has an invalid date-time format."
        ) from error


def check_number(items: tuple[str, Any]):
    """Check if row cell is a non-negative integer"""

    key, value = items
    try:
        converted = int(value)
    except ValueError as error:
        raise CSVValidationException(f"{key} is not an integer number.") from error

    if converted < 0:
        raise CSVValidationException(f"{key} cannot be a negative number.")


def check_float(items: tuple[str, Any]):
    """Check if row cell is a non-negative float"""

    key, value = items
    try:
        converted = float(value)
    except ValueError as error:
        raise CSVValidationException(f"{key} is not a float number.") from error

    if converted < 0:
        raise CSVValidationException(f"{key} cannot be a negative number.")
