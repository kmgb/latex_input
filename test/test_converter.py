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
            "^{ABDEGHIJKLMNOPRTUVW}": "ᴬᴮᴰᴱᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᴿᵀᵁⱽᵂ",
            "^{(=)+-}": "⁽⁼⁾⁺⁻",
            "^{}":      "",
            "_{}":      "",

            "\\epsilon\\varepsilon": "ϵε",
            "\\phi\\varphi": "ϕφ",

            "\\mathbb{Easy}":       "𝔼𝕒𝕤𝕪",
            "\\mathcal{Medium}":    "ℳℯ𝒹𝒾𝓊𝓂",
            "\\mathfrak{Hard}":     "ℌ𝔞𝔯𝔡",
            "\\mathfrak{123}":      "123",  # No actual conversion, fall back to input

            # Non-standard shorthands
            "\\b{boldtext}":        "𝐛𝐨𝐥𝐝𝐭𝐞𝐱𝐭",
            "\\i{italictext}":      "𝑖𝑡𝑎𝑙𝑖𝑐𝑡𝑒𝑥𝑡",
            "\\bi{bolditalic}":     "𝒃𝒐𝒍𝒅𝒊𝒕𝒂𝒍𝒊𝒄",
            "\\ib{italicbold}":     "𝒊𝒕𝒂𝒍𝒊𝒄𝒃𝒐𝒍𝒅",
            "\\i{italic\\b{bold}}": "𝑖𝑡𝑎𝑙𝑖𝑐𝒃𝒐𝒍𝒅",
            "\\i{italic}\\b{bold}": "𝑖𝑡𝑎𝑙𝑖𝑐𝐛𝐨𝐥𝐝",
            "\\ib{}":               "",
            "\\b{\\phi\\pi}":       "𝛟𝛑",
            "\\i{\\phi\\pi}":       "𝜙𝜋",
            "\\bi{\\phi\\pi}":      "𝝓𝝅",

            # Combinations
            "\\i{\\mathbb{Easy}}":      "𝔼𝕒𝕤𝕪",  # Note: i has no effect
            "\\b{\\mathbb{Easy}}":      "𝔼𝕒𝕤𝕪",  # Note: b has no effect
            "\\i{\\mathcal{Medium}}":   "ℳℯ𝒹𝒾𝓊𝓂",  # Note: i has no effect
            "\\b{\\mathcal{Medium}}":   "𝓜𝓮𝓭𝓲𝓾𝓶",
            "\\i{\\mathfrak{Hard}}":    "ℌ𝔞𝔯𝔡",  # Note: i has no effect
            "\\b{\\mathfrak{Hard}}":    "𝕳𝖆𝖗𝖉",
            "\\mathbb{\\i{Easy}}":      "𝐸𝑎𝑠𝑦",  # Note: mathbb has no effect
            "\\mathbb{\\b{Easy}}":      "𝐄𝐚𝐬𝐲",  # Note: mathbb has no effect
            "\\mathcal{\\i{Medium}}":   "𝑀𝑒𝑑𝑖𝑢𝑚",  # Note: mathcal has no effect
            "\\mathcal{\\b{Medium}}":   "𝓜𝓮𝓭𝓲𝓾𝓶",
            "\\mathfrak{\\b{Hard}}":    "𝕳𝖆𝖗𝖉",
            "\\mathfrak{\\i{Hard}}":    "𝐻𝑎𝑟𝑑",  # Note: mathfrak has no effect

            # Escapes
            "\\{":              "{",
            "\\}":              "}",
            "\\{\\}":           "{}",
            "\\\\":             "\\",

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
            "\\":               "ERROR",
        }

        for k, v in tests.items():
            try:
                self.assertEqual(latex_to_unicode(k), v, f"Failed on test for {k, v}")
            except AssertionError as e:
                self.fail(f"Exception raised on test for {k, v}: {e}")
