# Script Description
The main description and usage of the script is accessible by the following CLI command:

```shell
python -m solution -h
```

```
usage: python -m solution [-h] [--bags BAGS] [--reverse] [--min-layover MIN_LAYOVER] [--max-layover MAX_LAYOVER] [--start-date START_DATE] csv origin destination

This script prints out a structured list of all flight combinations for a given flight data in a form of csv file for a selected route between airports A -> B, sorted by the final price for     
the trip, in json format. Example usage: `python -m solution test_data/example0.csv WIW RFZ --bags=1`

positional arguments:
  csv                   Path to the .csv file. Example: test_data/example0.csv
  origin                Origin airport code.
  destination           Destination airport code.

options:
  -h, --help                    show this help message and exit
  --bags BAGS                   Number of requested bags. Optional (defaults to 0).
  --reverse                     Is it a return flight? Optional (defaults to false).
  --min-layover MIN_LAYOVER     The minimum layover time between arrive and departure time should not be less than X hours. Optional (defaults to 1).
  --max-layover MAX_LAYOVER     The maximum layover time between arrive and departure time should not be more than X hours. Optional (defaults to 6).
  --start-date START_DATE       The start date of your trip in YYYY-MM-DD date format. Optional.
```

## Data Structure
The scripts only works on the following CSV data structure:
- `flight_no`: Flight number.
- `origin`, `destination`: Airport codes.
- `departure`, `arrival`: Dates and times of the departures/arrivals.
- `base_price`, `bag_price`: Prices of the ticket and one piece of baggage.
- `bags_allowed`: Number of allowed pieces of baggage for the flight.

## Implemented Search Restrictions
- By default, the search is performed on all available combinations, according to search parameters.
- In case of a combination of A -> B -> C, the layover time in B is **not be less than 1 hour and more than 6 hours** by default.
- There are no repeating airports in the same trip:
    - A -> B -> A -> C is not a valid combination for search A -> C.
- Output is sorted by the final price of the trip.

## Project Structure
- `argparser.py`: Contains the argument CLI argument parsing logic
- `flighthandler.py`: Contains all models and logic necessary for the trip calculations
- `csvreader.py`: Enhanced csv reader module for parsing, validating and checking flight data
- `solution.py`: The main script that should be called, it glues all modules to work on the solution
- `test_solution.py`: Some basic test cases, mainly happy paths
- `test_data`: Directory contains the example csv files and some generated json files for unit testing

## Example usages
Only with mandatory arguments:

```shell
python -m solution test_data/example0.csv WIW RFZ
```

Let's bring 2 bags:
```shell
python -m solution test_data/example0.csv WIW RFZ --bags=2
```

And see how we can get back:
```shell
python -m solution test_data/example0.csv WIW RFZ --bags=2 --reverse
```

Let's check flights on a given date:
```shell
python -m solution test_data/example0.csv WIW RFZ --bags=2 --start-date=2021-09-04
```

With other layover hours:
```shell
python -m solution test_data/example1.csv DHE NIZ --bags=1 --start-date=2021-09-04 --min-layover=12 --max-layover=48
```

## Tests
There are some basic test cases prepared, to run them use the following command:
```shell
python -m unittest -v
```

## Error Handling
In case of wrong or missing argument is provided:

```shell
usage: python -m solution [-h] [--bags BAGS] [--reverse] [--min-layover MIN_LAYOVER] [--max-layover MAX_LAYOVER]
                          [--start-date START_DATE]
                          csv origin destination
python -m solution: error: the following arguments are required: destination
````
```shell
usage: python -m solution [-h] [--bags BAGS] [--reverse] [--min-layover MIN_LAYOVER] [--max-layover MAX_LAYOVER]
                          [--start-date START_DATE]
                          csv origin destination
python -m solution: error: argument --bags: invalid int value: 'x'
```

In case of incorrect data in the csv file:
```shell
error: Incorrect CSV headers. The following headers are expected: flight_no, origin, destination, departure, arrival, base_price, bag_price, bags_allowed
error: wrong value in CSV file at row [2]: bags_allowed is not an integer number.
error: wrong value in CSV file at row [16]: departure has an invalid date-time format.
error: wrong value in CSV file at row [18]: flight_no cannot be an empty string.
error: wrong value in CSV file at row [4]: base_price cannot be a negative number.
```

## Supported Arguments
| Argument name   | type    | Description                        | Notes                          |
|-----------------|---------|------------------------------------|--------------------------------|
| `csv`           | string  | Origin airport code                | Positional, mandatory          |
| `origin`        | string  | Origin airport code                | Positional, mandatory          |
| `destination`   | string  | Destination airport code           | Positional, mandatory          |
| `--bags`        | integer | Number of requested bags           | Optional (defaults to 0)       |
| `--return`      | boolean | Is it a return flight?             | Optional (defaults to false)   |
| `--start-date`  | string  | Start date of the trip             | Optional (format YYY-MM-DD)    |
| `--min-layover` | integer | Min. layover between two flights   | Optional (defaults to 1 hour)  |
| `--max-layover` | integer | Max. layover between two flights   | Optional (defaults to 6 hours) |


## Output
The output is json string of trips sorted by price. The trip has the following schema:

| Field          | Description                                                   |
|----------------|---------------------------------------------------------------|
| `flights`      | A list of flights in the trip according to the input dataset. |
| `origin`       | Origin airport of the trip.                                   |
| `destination`  | The final destination of the trip.                            |
| `bags_allowed` | The number of allowed bags for the trip.                      |
| `bags_count`   | The searched number of bags.                                  |
| `total_price`  | The total price for the trip.                                 |
| `travel_time`  | The total travel time.                                        |

Example result:
```json
[
    {
        "flights": [
            {
                "flight_no": "ZH214",
                "origin": "WIW",
                "destination": "RFZ",
                "departure": "2021-09-01T23:20:00",
                "arrival": "2021-09-02T03:50:00",
                "base_price": 168.0,
                "bag_price": 12,
                "bags_allowed": 2
            }
        ],
        "bags_allowed": 2,
        "bags_count": 2,
        "destination": "RFZ",
        "origin": "WIW",
        "total_price": 192.0,
        "travel_time": "4:30:00"
    },
    {
        "flights": [
            {
                "flight_no": "ZH214",
                "origin": "WIW",
                "destination": "RFZ",
                "departure": "2021-09-04T23:20:00",
                "arrival": "2021-09-05T03:50:00",
                "base_price": 168.0,
                "bag_price": 12,
                "bags_allowed": 2
            }
        ],
        "bags_allowed": 2,
        "bags_count": 2,
        "destination": "RFZ",
        "origin": "WIW",
        "total_price": 192.0,
        "travel_time": "4:30:00"
    },
    {
        "flights": [
            {
                "flight_no": "ZH214",
                "origin": "WIW",
                "destination": "RFZ",
                "departure": "2021-09-09T23:20:00",
                "arrival": "2021-09-10T03:50:00",
                "base_price": 168.0,
                "bag_price": 12,
                "bags_allowed": 2
            }
        ],
        "bags_allowed": 2,
        "bags_count": 2,
        "destination": "RFZ",
        "origin": "WIW",
        "total_price": 192.0,
        "travel_time": "4:30:00"
    }
]
```

