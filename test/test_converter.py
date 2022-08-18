from latex_input.latex_converter import latex_to_unicode

import unittest


class TestConverter(unittest.TestCase):
    def setUp(self):
        pass

    def test_converter(self):
        tests = {
            "":         "",
            "a":        "a",
            "^a":       "ᵃ",
            "^ab":      "ᵃb",
            "^{ab}":    "ᵃᵇ",
            "r^e^{al} _t_{al}_{k}": "rᵉᵃˡ ₜₐₗₖ",
            "^{abcdefghijklmnopqrstuvwxyz0123456789}": "ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖ𐞥ʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹",

            "\\epsilon\\varepsilon": "ϵε",
            "\\phi\\varphi": "ϕφ",

            "\\mathbb{Easy}":       "𝔼𝕒𝕤𝕪",
            "\\mathcal{Medium}":    "ℳℯ𝒹𝒾𝓊𝓂",
            "\\mathfrak{Hard}":     "ℌ𝔞𝔯𝔡",

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
            "\\mathfrak{123}":  "ERROR",
        }

        for k, v in tests.items():
            try:
                self.assertEqual(latex_to_unicode(k), v, f"Failed on test for {k, v}")
            except AssertionError as e:
                self.fail(f"Exception raised on test for {k, v}: {e}")
