import unittest
import solution
import json


class TestSolution(unittest.TestCase):
    def setUp(self):
        solution.MIN_LAYOVER = 1
        solution.MAX_LAYOVER = 6
        solution.REVERSE = False
        solution.BAGS = 0
        solution.START_DATE = "1900-01-01"

    def test_0_wiw_rfz_2_f(self):
        solution.CSV = "test_data/example0.csv"
        solution.FROM = "WIW"
        solution.TO = "RFZ"
        solution.BAGS = 2
        solution.REVERSE = False
        result = solution.main()
        calculated = json.loads(result)
        with open("test_data/0_wiw_rfz_2_f.json") as file:
            prepared = json.load(file)
        self.assertCountEqual(calculated, prepared)

    def test_0_ecv_wiw_1_f_x_24(self):
        solution.CSV = "test_data/example0.csv"
        solution.FROM = "ECV"
        solution.TO = "WIW"
        solution.BAGS = 1
        solution.REVERSE = False
        solution.MAX_LAYOVER = 24
        result = solution.main()
        calculated = json.loads(result)
        with open("test_data/0_ecv_wiw_1_f_x_24.json") as file:
            prepared = json.load(file)
        self.assertCountEqual(calculated, prepared)

    def test_0_wiw_rfz_2_t(self):
        solution.CSV = "test_data/example0.csv"
        solution.FROM = "WIW"
        solution.TO = "RFZ"
        solution.BAGS = 2
        solution.REVERSE = True
        result = solution.main()
        calculated = json.loads(result)
        with open("test_data/0_wiw_rfz_2_t.json") as file:
            prepared = json.load(file)
        self.assertCountEqual(calculated, prepared)

    def test_0_wiw_rfz_1_f_x_x_2021_09_04(self):
        solution.CSV = "test_data/example0.csv"
        solution.FROM = "WIW"
        solution.TO = "RFZ"
        solution.BAGS = 1
        solution.REVERSE = False
        solution.START_DATE = "2021-09-04"
        result = solution.main()
        calculated = json.loads(result)
        with open("test_data/0_wiw_rfz_1_f_x_x_2021_09_04.json") as file:
            prepared = json.load(file)
        self.assertCountEqual(calculated, prepared)

    def test_1_dhe_niz_1_f(self):
        solution.CSV = "test_data/example1.csv"
        solution.FROM = "DHE"
        solution.TO = "NIZ"
        solution.BAGS = 1
        solution.REVERSE = False
        result = solution.main()
        calculated = json.loads(result)
        with open("test_data/1_dhe_niz_1_f.json") as file:
            prepared = json.load(file)
        self.assertCountEqual(calculated, prepared)

    def test_2_iut_lom_2_f(self):
        solution.CSV = "test_data/example2.csv"
        solution.FROM = "IUT"
        solution.TO = "LOM"
        solution.BAGS = 2
        solution.REVERSE = False
        result = solution.main()
        calculated = json.loads(result)
        with open("test_data/2_iut_lom_2_f.json") as file:
            prepared = json.load(file)
        self.assertCountEqual(calculated, prepared)

    def test_3_bpz_nnb_1_f(self):
        solution.CSV = "test_data/example3.csv"
        solution.FROM = "BPZ"
        solution.TO = "NNB"
        solution.BAGS = 1
        solution.REVERSE = False
        result = solution.main()
        calculated = json.loads(result)
        with open("test_data/3_bpz_nnb_1_f.json") as file:
            prepared = json.load(file)
        self.assertCountEqual(calculated, prepared)

    def test_3_jbn_vvh_1_t(self):
        solution.CSV = "test_data/example3.csv"
        solution.FROM = "JBN"
        solution.TO = "VVH"
        solution.BAGS = 2
        solution.REVERSE = True
        result = solution.main()
        calculated = json.loads(result)
        with open("test_data/3_jbn_vvh_2_t.json") as file:
            prepared = json.load(file)
        self.assertCountEqual(calculated, prepared)


if __name__ == "__main__":
    unittest.main()
