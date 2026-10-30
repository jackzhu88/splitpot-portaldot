import unittest
from splitmath import parse_shares, to_planck, split_amounts


class SplitMathTest(unittest.TestCase):
    def test_testnet_run_amounts(self):
        # matches the public PortaldotV3 run: 6 tPOT 50/30/20 -> 3 / 1.8 / 1.2
        self.assertEqual(split_amounts(to_planck("6", 14), [50, 30, 20]),
                         [300000000000000, 180000000000000, 120000000000000])

    def test_sum_is_exact_with_dust(self):
        a = split_amounts(10, [33, 33, 34])
        self.assertEqual(sum(a), 10)
        a = split_amounts(7, [50, 50])
        self.assertEqual(a, [3, 4])

    def test_no_float_error(self):
        self.assertEqual(to_planck("0.1", 14), 10 ** 13)

    def test_bad_shares(self):
        for bad in ["50,30", "100", "60,50,-10", "a,b", "50,50,0"]:
            with self.assertRaises(ValueError):
                parse_shares(bad)

    def test_bad_amount(self):
        for bad in ["0", "-1", "abc", "0.000000000000001"]:
            with self.assertRaises(ValueError):
                to_planck(bad, 14)


if __name__ == "__main__":
    unittest.main()
