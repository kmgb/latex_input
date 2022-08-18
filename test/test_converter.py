from latex_input.latex_converter import latex_to_unicode

import unittest


class TestConverter(unittest.TestCase):
    def setUp(self):
        pass

    def test_converter(self):
        tests = {
            "":         "",
            "a":        "a",
            "^a":       "ª",
            "^ab":      "ªb",
            "^{ab}":    "ªᵇ",
            "r^e^{al} _t_{al}_{k}": "rᵉªˡ ₜₐₗₖ",
            "^{abcdefghijklmnopqrstuvwxyz0123456789}": "ªᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿºᵖ𐞥ʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹",

            "\\epsilon\\varepsilon": "ϵε",
            "\\phi\\varphi": "ϕφ",

            # Broken inputs
            "_":                "ERROR",
            "^":                "ERROR",
            "^{7654":           "ERROR",
            "_{7654":           "ERROR",
            "\\var{abc":        "ERROR",
            "\\invalid":        "ERROR",
            "\\invalid{abc}":   "ERROR",
            "\\invalid{}":      "ERROR",
            "\\{}":             "ERROR",
            "\\{":              "ERROR",
            "\\}":              "ERROR",
            "\\":               "ERROR",
        }

        for k, v in tests.items():
            try:
                self.assertEqual(latex_to_unicode(k), v, f"Failed on test for {k, v}")
            except AssertionError as e:
                self.fail(f"Exception raised on test for {k, v}: {e}")
