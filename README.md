# Python weekend entry task

**Write a python script/module/package, that for a given flight data in a form of `csv` file (check the examples), prints out a structured list of all flight combinations for a selected route between airports A -> B, sorted by the final price for the trip.**

### Description
You've been provided with some semi-randomly generated example csv datasets you can use to test your solution. The datasets have following columns:
- `flight_no`: Flight number.
- `origin`, `destination`: Airport codes.
- `departure`, `arrival`: Dates and times of the departures/arrivals.
- `base_price`, `bag_price`: Prices of the ticket and one piece of baggage.
- `bags_allowed`: Number of allowed pieces of baggage for the flight.

In addition to the dataset, your script will take some additional arguments as input:

| Argument name | type    | Description              | Notes                        |
|---------------|---------|--------------------------|------------------------------|
| `origin`      | string  | Origin airport code      |                              |
| `destination` | string  | Destination airport code |                              |

### Search restrictions
- By default you're performing search on ALL available combinations, according to search parameters.
- In case of a combination of A -> B -> C, the layover time in B should **not be less than 1 hour and more than 6 hours**.
- No repeating airports in the same trip!
    - A -> B -> A -> C is not a valid combination for search A -> C.
- Output is sorted by the final price of the trip.

#### Optional arguments
You may add any number of additional search parameters to boost your chances to attend. Here are 2 recommended ones:

| Argument name | type    | Description              | Notes                        |
|---------------|---------|--------------------------|------------------------------|
| `bags`        | integer | Number of requested bags | Optional (defaults to 0)     |
| `return`      | boolean | Is it a return flight?   | Optional (defaults to false) |

##### Performing return trip search
Example input (assuming `solution.py` is the main module):
```
python -m solution example/example0.csv RFZ WIW --bags=1 --return
```
will perform a search RFZ -> WIW -> RFZ for flights which allow at least 1 piece of baggage.

- **NOTE:** Since WIW is in this case the final destination for one part of the trip, the layover rule does not apply.

#### Output
The output will be a json-compatible structured list of trips sorted by price. The trip has the following schema:
| Field          | Description                                                   |
|----------------|---------------------------------------------------------------|
| `flights`      | A list of flights in the trip according to the input dataset. |
| `origin`       | Origin airport of the trip.                                   |
| `destination`  | The final destination of the trip.                            |
| `bags_allowed` | The number of allowed bags for the trip.                      |
| `bags_count`   | The searched number of bags.                                  |
| `total_price`  | The total price for the trip.                                 |
| `travel_time`  | The total travel time.                                        |

**For more information, check the example section.**

### Points of interest
Assuming your solution is working, we'll be additionally judging based on following skills:
- input, output - what if we input garbage?
- modules, packages & code structure (hint: it's easy to overdo it)
- usage of standard library and built-in data structures
- code readability, clarity, used conventions, documentation and comments

## Requirements and restrictions
- **Your solution needs to contain a README file describing what it does and how to run it.**
- Only the standard library is allowed, no 3rd party packages, notebooks, specialized distros (Conda) etc.
- The code should run as is, no environment setup should be required.

## Submissions
Follow the instructions you received in the email.

## Example behaviour

Let's imagine we wrote our solution into one file, `solution.py` and our datatset is in `data.csv`.
We want to test the script by performing a flight search on route BTW -> REJ (we know the airports are present in the dataset) with one bag. We run the thing:

```bash
python -m solution data.csv BTW REJ --bags=1
```
and get the following result:

```json
[
    {
        "flights": [
            {
                "flight_no": "XC233",
                "origin": "BTW",
                "destination": "WTF",
                "departure": "2021-09-02T05:50:00",
                "arrival": "2021-09-02T8:20:00",
                "base_price": 67.0,
                "bag_price": 7.0,
                "bags_allowed": 2
            },
            {
                "flight_no": "VJ832",
                "origin": "WTF",
                "destination": "REJ",
                "departure": "2021-09-02T11:05:00",
                "arrival": "2021-09-02T12:45:00",
                "base_price": 31.0,
                "bag_price": 5.0,
                "bags_allowed": 1
            }
        ],
        "bags_allowed": 1,
        "bags_count": 1,
        "destination": "REJ",
        "origin": "BTW",
        "total_price": 110.0,
        "travel_time": "6:55:00"
    },
    {
        "flights": [
            {
                "flight_no": "JV042",
                "origin": "BTW",
                "destination": "REJ",
                "departure": "2021-09-01T17:35:00",
                "arrival": "2021-09-01T21:05:00",
                "base_price": 216.0,
                "bag_price": 11.0,
                "bags_allowed": 2
            }
        ],
        "bags_allowed": 2,
        "bags_count": 1,
        "destination": "REJ",
        "origin": "BTW",
        "total_price": 227.0,
        "travel_time": "3:30:00"
    }
]
```

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

#### Arguments
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


#### Output
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
        "fligths": [
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
        "fligths": [
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
        "fligths": [
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

#### Example usages
```shell
python -m solution test_data/example0.csv WIW RFZ
python -m solution test_data/example0.csv WIW RFZ --bags=2
python -m solution test_data/example0.csv WIW RFZ --bags=2 --reverse
python -m solution test_data/example0.csv WIW RFZ --bags=2 --start-date=2021-09-04
python -m solution test_data/example0.csv WIW RFZ --bags=2 --start-date=2021-09-04 --min-layover=10
python -m solution test_data/example1.csv DHE NIZ --bags=1 --start-date=2021-09-04 --min-layover=12 --max-layover=48
```