"""Parser module for CLI command line"""

from datetime import datetime
import argparse


def check_number(number: str) -> int:
    """Check if a value is a non-negative integer"""

    try:
        converted = int(number)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid int value: '{number}'") \
            from error
    if converted < 0:
        raise argparse.ArgumentTypeError(f"not a positive number: '{number}'")
    if converted > 999:
        raise argparse.ArgumentTypeError(f"too much: '{number}'")  # :)
    return converted


def check_date(date_string: str) -> str:
    """Check if value in correct date time format"""

    try:
        datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            f"invalid date format: '{date_string}'"
        ) from error
    return date_string


def get_args() -> argparse.Namespace:
    """Collect the input provided from CLI, handle the default values and
    errors """

    parser = argparse.ArgumentParser(
        description="This script prints out a structured list of all flight "
                    "combinations for a selected route between "
                    "airports A -> B, sorted by the final price for the trip, "
                    "in json format. As input, the script "
                    "uses flight data given in a form of csv file. Example "
                    "usage: `python -m solution "
                    "test_data/example0.csv WIW RFZ --bags=1`",
        prog="python -m solution",
    )

    parser.add_argument(
        "csv",
        action="store",
        type=str,
        help="Path to the .csv file. Example: test_data/example0.csv",
    )
    parser.add_argument("origin", action="store", type=str, help="Origin "
                                                                 "airport "
                                                                 "code.")
    parser.add_argument(
        "destination", action="store", type=str, help="Destination airport "
                                                      "code. "
    )
    parser.add_argument(
        "--bags",
        action="store",
        type=check_number,
        default=0,
        help="Number of requested bags. Optional (defaults to 0).",
    )
    parser.add_argument(
        "--reverse", "-r",
        action="store_true",
        default=False,
        help="Is it a return flight? Optional (defaults to false).",
    )
    parser.add_argument(
        "--min-layover",
        action="store",
        default=1,
        type=check_number,
        help="The minimum layover time between arrival and departure time "
             "should not be less than X hours. Optional (defaults to 1).",
    )
    parser.add_argument(
        "--max-layover",
        action="store",
        default=6,
        type=check_number,
        help="The maximum layover time between arrival and departure time "
             "should not be more than X hours. Optional (defaults to 6).",
    )
    parser.add_argument(
        "--start-date",
        action="store",
        type=check_date,
        help="The start date of your trip in YYYY-MM-DD date format. Optional.",
        default="1900-01-01",
    )
    return parser.parse_args()
