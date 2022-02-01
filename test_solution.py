import unittest
import solution
import json


class TestSolution(unittest.TestCase):
    def setUp(self):
        solution.namespace.min_layover = 1
        solution.namespace.max_layover = 6
        solution.namespace.reverse = False
        solution.namespace.bags = 0
        solution.namespace.start_date = "1900-01-01"

    def test_0_wiw_rfz_2_f(self):
        solution.namespace.csv = "test_data/example0.csv"
        solution.namespace.origin = "WIW"
        solution.namespace.destination = "RFZ"
        solution.namespace.bags = 2
        solution.namespace.reverse = False
        result = solution.main()
        calculated = json.loads(result)
        with open("test_data/0_wiw_rfz_2_f.json") as file:
            prepared = json.load(file)
        self.assertCountEqual(calculated, prepared)

    def test_0_ecv_wiw_1_f_x_24(self):
        solution.namespace.csv = "test_data/example0.csv"
        solution.namespace.origin = "ECV"
        solution.namespace.destination = "WIW"
        solution.namespace.bags = 1
        solution.namespace.reverse = False
        solution.namespace.max_layover = 24
        result = solution.main()
        calculated = json.loads(result)
        with open("test_data/0_ecv_wiw_1_f_x_24.json") as file:
            prepared = json.load(file)
        self.assertCountEqual(calculated, prepared)

    def test_0_wiw_rfz_2_t(self):
        solution.namespace.csv = "test_data/example0.csv"
        solution.namespace.origin = "WIW"
        solution.namespace.destination = "RFZ"
        solution.namespace.bags = 2
        solution.namespace.reverse = True
        result = solution.main()
        calculated = json.loads(result)
        with open("test_data/0_wiw_rfz_2_t.json") as file:
            prepared = json.load(file)
        self.assertCountEqual(calculated, prepared)

    def test_0_wiw_rfz_1_f_x_x_2021_09_04(self):
        solution.namespace.csv = "test_data/example0.csv"
        solution.namespace.origin = "WIW"
        solution.namespace.destination = "RFZ"
        solution.namespace.bags = 1
        solution.namespace.reverse = False
        solution.namespace.start_date = "2021-09-04"
        result = solution.main()
        calculated = json.loads(result)
        with open("test_data/0_wiw_rfz_1_f_x_x_2021_09_04.json") as file:
            prepared = json.load(file)
        self.assertCountEqual(calculated, prepared)

    def test_1_dhe_niz_1_f(self):
        solution.namespace.csv = "test_data/example1.csv"
        solution.namespace.origin = "DHE"
        solution.namespace.destination = "NIZ"
        solution.namespace.bags = 1
        solution.namespace.reverse = False
        result = solution.main()
        calculated = json.loads(result)
        with open("test_data/1_dhe_niz_1_f.json") as file:
            prepared = json.load(file)
        self.assertCountEqual(calculated, prepared)

    def test_2_iut_lom_2_f(self):
        solution.namespace.csv = "test_data/example2.csv"
        solution.namespace.origin = "IUT"
        solution.namespace.destination = "LOM"
        solution.namespace.bags = 2
        solution.namespace.reverse = False
        result = solution.main()
        calculated = json.loads(result)
        with open("test_data/2_iut_lom_2_f.json") as file:
            prepared = json.load(file)
        self.assertCountEqual(calculated, prepared)

    def test_3_bpz_nnb_1_f(self):
        solution.namespace.csv = "test_data/example3.csv"
        solution.namespace.origin = "BPZ"
        solution.namespace.destination = "NNB"
        solution.namespace.bags = 1
        solution.namespace.reverse = False
        result = solution.main()
        calculated = json.loads(result)
        with open("test_data/3_bpz_nnb_1_f.json") as file:
            prepared = json.load(file)
        self.assertCountEqual(calculated, prepared)

    def test_3_jbn_vvh_1_t(self):
        solution.namespace.csv = "test_data/example3.csv"
        solution.namespace.origin = "JBN"
        solution.namespace.destination = "VVH"
        solution.namespace.bags = 2
        solution.namespace.reverse = True
        result = solution.main()
        calculated = json.loads(result)
        with open("test_data/3_jbn_vvh_2_t.json") as file:
            prepared = json.load(file)
        self.assertCountEqual(calculated, prepared)


if __name__ == "__main__":
    unittest.main()
