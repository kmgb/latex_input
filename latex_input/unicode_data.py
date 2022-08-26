from latex_input.parse_unicode_data import (
    CharacterFontVariant, character_font_variants, subscript_mapping, superscript_mapping
)

# Manual fixes
superscript_mapping["α"] = "ᵅ"
superscript_mapping["ϵ"] = "ᵋ"
superscript_mapping["ι"] = "ᶥ"
superscript_mapping["ϕ"] = "ᶲ"

latex_symbol_list = {
    # Greek letters
    "Alpha":    "\u0391",
    "Beta":     "\u0392",
    "Gamma":    "\u0393",
    "Delta":    "\u0394",
    "Epsilon":  "\u0395",
    "Zeta":     "\u0396",
    "Eta":      "\u0397",
    "Theta":    "\u0398",
    "Iota":     "\u0399",
    "Kappa":    "\u039A",
    "Lambda":   "\u039B",
    "Mu":       "\u039C",
    "Nu":       "\u039D",
    "Xi":       "\u039E",
    "Omicron":  "\u039F",
    "Pi":       "\u03A0",
    "Rho":      "\u03A1",
    "Sigma":    "\u03A3",
    "Tau":      "\u03A4",
    "Upsilon":  "\u03A5",
    "Phi":      "\u03A6",
    "Chi":      "\u03A7",
    "Psi":      "\u03A8",
    "Omega":    "\u03A9",
    "alpha":    "\u03B1",
    "beta":     "\u03B2",
    "gamma":    "\u03B3",
    "delta":    "\u03B4",
    "epsilon":  "\u03F5",  # NOTE: This is the lunate form by default. Varepsilon is the reversed-3
    "zeta":     "\u03B6",
    "eta":      "\u03B7",
    "theta":    "\u03B8",
    "iota":     "\u03B9",
    "kappa":    "\u03BA",
    "lambda":   "\u03BB",
    "mu":       "\u03BC",
    "nu":       "\u03BD",
    "xi":       "\u03BE",
    "omicron":  "\u03BF",
    "pi":       "\u03C0",
    "rho":      "\u03C1",
    "sigma":    "\u03C3",
    "tau":      "\u03C4",
    "upsilon":  "\u03C5",
    "phi":      "\u03D5",  # NOTE: This is the closed form by default. Varphi is the open form
    "chi":      "\u03C7",
    "psi":      "\u03C8",
    "omega":    "\u03C9",

    # Greek letter variants
    "varepsilon":   "\u03B5",  # ε
    "vartheta":     "\u03D1",  # ϑ
    "varpi":        "\u03D6",  # ϖ
    "varrho":       "\u03F1",  # ϱ
    "varsigma":     "\u03C2",  # ς
    "varphi":       "\u03C6",  # φ

    # Cardinality Hebrew math symbols
    "aleph":        "\u2135",  # ℵ
    "beth":         "\u2136",  # ℶ
    "gimel":        "\u2137",  # ℷ
    "dalet":        "\u2138",  # ℸ

    # Math and logic
    "neg":          "\u00AC",  # ¬ Negation
    "pm":           "\u00B1",  # ± Plus or minus sign
    "mp":           "\u2213",  # ∓ Minus or plus sign
    "times":        "\u00D7",  # × Multiplication / cross product
    "div":          "\u00F7",  # ÷ Obelus division sign
    "forall":       "\u2200",  # ∀ For all, universal quantification
    "partial":      "\u2202",  # ∂ Partial derivative symbol
    "exists":       "\u2203",  # ∃ There exists, existential quantification
    "varnothing":   "\u2205",  # ∅ Empty set symbol
    "nabla":        "\u2207",  # ∇ Gradient, divergence, curl
    "in":           "\u2208",  # ∈ Element of
    "infty":        "\u221E",  # ∞ Infinity symbol
    "land":         "\u2227",  # ∧ Logical conjunction
    "lor":          "\u2228",  # ∨ Logical disjunction
    "int":          "\u222B",  # ∫ Integral
    "iint":         "\u222C",  # ∬ Double integral
    "iiint":        "\u222D",  # ∭ Triple integral
    "oint":         "\u222E",  # ∮ Closed integral
    "oiint":        "\u222F",  # ∯ Closed double integral
    "oiiint":       "\u2230",  # ∰ Closed triple integral
    "therefore":    "\u2234",  # ∴ Therefore symbol
    "because":      "\u2235",  # ∵ Since symbol
    "approx":       "\u2248",  # ≈ Approx equal
    "neq":          "\u2260",  # ≠ Not equal
    "equiv":        "\u2261",  # ≡ Equivalence operator
    "oplus":        "\u2295",  # ⊕
    "otimes":       "\u2297",  # ⊗
    "true":         "\u22A4",  # ⊤ Truth symbol
    "false":        "\u22A5",  # ⊥ Falsity symbol
    "models":       "\u22A8",  # ⊨ Double turnstile
    "nmodels":      "\u22AD",  # ⊭ Negated double turnstile
    "cdot":         "\u22C5",  # ⋅ Dot product operator
    "langle":       "\u27E8",  # ⟨ Dot product, inner product space
    "rangle":       "\u27E9",  # ⟩
    "implies":      "\u27F9",  # ⟹ Implies arrow
    "iff":          "\u27FA",  # ⟺ If and only if arrow

    # Number set shorthands (mathbb) -- useful but non-standard
    "Complex":      "\u2102",  # ℂ
    "N":            "\u2115",  # ℕ
    "Q":            "\u211A",  # ℚ
    "R":            "\u211D",  # ℝ
    "Z":            "\u2124",  # ℤ

    "Im":           "\u2111",  # ℑ
    "Re":           "\u211C",  # ℜ

    # Shapes
    "square":       "\u25A1",  # □

    # Music symbols
    "flat":         "\u266D",  # ♭
    "natural":      "\u266E",  # ♮
    "sharp":        "\u266F",  # ♯
    "segno":        "\U0001D10B",  # 𝄋 Non-standard
    "coda":         "\U0001D10C",  # 𝄌 Non-standard
}
