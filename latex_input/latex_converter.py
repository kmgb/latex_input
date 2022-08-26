import copy
from dataclasses import dataclass
import re

from latex_input.parse_unicode_data import (
    superscript_mapping, subscript_mapping, character_font_variants
)


@dataclass
class FontContext:
    is_bold: bool = False
    is_double_struck: bool = False
    is_fraktur: bool = False
    is_italic: bool = False
    is_sans_serif: bool = False
    is_script: bool = False
    is_subscript: bool = False
    is_superscript: bool = False

    def is_trivial(self) -> bool:
        return not (self.is_bold or self.is_double_struck or
                    self.is_fraktur or self.is_italic or
                    self.is_sans_serif or self.is_script or
                    self.is_subscript or self.is_superscript)


# HACK: Global font context stack used for AST conversions
font_context_stack = list[FontContext]()


def latex_to_unicode(tex, context=FontContext()) -> str:
    parser = LatexRDescentParser()

    font_context_stack.append(context)

    try:
        result = parser.parse(tex)
        print(result)
        return result.convert()
    except Exception as e:
        print(f"Failed to convert {tex}, Error = {e}")
        return "ERROR"
    finally:
        font_context_stack.pop()


def _map_text(mapping: dict[str, str], text: str) -> str:
    # Iterate all characters in text and convert them using map
    return "".join([mapping.get(c, c) for c in text])


def to_superscript_form(t: str) -> str:
    return _map_text(superscript_mapping, t)


def to_subscript_form(t: str) -> str:
    return _map_text(subscript_mapping, t)


@dataclass
class ASTNode:
    def convert(self) -> str:
        assert False, "Not implemented"


@dataclass
class ASTLatex(ASTNode):
    nodes: list[ASTNode]

    def convert(self) -> str:
        return "".join(n.convert() for n in self.nodes)


@dataclass
class ASTLiteral(ASTNode):
    text: str

    def convert(self) -> str:
        context = font_context_stack[-1]

        text = self.perform_character_replacements()

        if context.is_trivial():
            return text

        if context.is_superscript:
            return to_superscript_form(text)

        elif context.is_subscript:
            return to_subscript_form(text)

        output = ""
        for basechar in text:
            variants = character_font_variants.get(basechar, [])
            conversion = ""

            variant_candidates = [x for x in variants if (
                x.is_bold == context.is_bold
                and x.is_double_struck == context.is_double_struck
                and x.is_fraktur == context.is_fraktur
                and x.is_italic == context.is_italic
                and x.is_sans_serif == context.is_sans_serif
                and x.is_script == context.is_script
            )]

            if not variant_candidates:
                print(f"No conversion found for {basechar} with context {context}")
                conversion = basechar
            else:
                # Prefer mathematical variants, if they exist. Otherwise just choose the first
                conversion = next(
                    (x for x in variant_candidates if x.is_mathematical),
                    variant_candidates[0]
                ).text

            output += conversion

        return output

    def perform_character_replacements(self) -> str:
        text = self.text

        # Dashes
        # FIXME: Text-mode only
        text = text.replace("---", "\u2014")  # Three dash -> Em dash
        text = text.replace("--", "\u2013")   # Two dash -> En dash
        # FIXME: Math-mode only
        text = text.replace("-", "\u2212")    # One dash -> Minus sign

        # Quotes to Lagrange's notation
        # FIXME: Math-mode only
        text = text.replace("''''", "\u2057")
        text = text.replace("'''", "\u2034")
        text = text.replace("''", "\u2033")
        text = text.replace("'", "\u2032")

        # Misc
        # TODO: Is this preferred anyways? Causes weird rendering for some applications
        # for example, browsers render 2/3 in a good way, others break
        # FIXME: Math-mode only
        text = text.replace("/", "\u2044")

        return text


class LatexRDescentParser:
    r"""
    Recursive descent parser that employs the following grammar rules:
    LaTeX   -> Expr*
    Expr    -> ε | Text | BSItem | Macro
    Macro   -> (\Text|^|_){Expr} | ^Char | _Char
    BSItem  -> \Text
    Text    -> Char+
    Char    -> (?:[a-zA-Z0-9 \!@]|(?:\\[\\\^_\{}]))
    """
    expression = ""
    index = 0
    char_regex = re.compile(r"(?:[a-zA-Z0-9 =\!\-+\()\[\]<>/]|(?:\\[\\\^_\{}]))")
    text_regex = re.compile(r"(?:[a-zA-Z0-9 =\!\-+\()\[\]<>/]|(?:\\[\\\^_\{}]))+")

    def parse(self, expression) -> ASTLatex:
        self.expression = expression
        self.index = 0
        nodes = []

        while self.index < len(self.expression):
            nodes.append(self._expr())

        return ASTLatex(nodes)

    def peek(self) -> str:
        if self.index >= len(self.expression):
            return ""

        return self.expression[self.index]

    def try_consume(self, expr) -> str | None:
        m = re.match(expr, self.expression[self.index:])
        if not m:
            return None

        self.index += m.end()

        return m.group()

    def consume(self, expr) -> str:
        c = self.try_consume(expr)
        assert c

        return c

    def try_consume_text(self) -> str | None:
        c = self.try_consume(self.text_regex)

        if c:
            c = re.sub(r"\\(.)", r"\1", c)  # Remove escape backslashes

        return c

    def consume_text(self) -> str:
        text = self.try_consume_text()
        assert text

        return text

    def consume_char(self) -> str:
        return self.consume(self.char_regex)

    def _expr(self) -> ASTNode:
        if self.index >= len(self.expression):
            return ASTLiteral("")

        text = self.try_consume_text()
        if text:
            return ASTLiteral(text)

        if self.peek() in ["\\", "^", "_"]:
            return self._macro()

        return ASTLiteral(self.consume_text())

    def _macro(self) -> ASTNode:
        function = self.consume(r"[\\^_]")

        single_char_mode = False

        if function == "\\":
            function = self.consume_text()

        if function in ["^", "_"]:
            single_char_mode = True

        maybe_expr: list[ASTNode] | None

        if self.peek() == "{":
            self.consume("{")

            maybe_expr = []
            while self.peek() not in ["}", ""]:
                maybe_expr.append(self._expr())

            self.consume("}")
        else:
            if single_char_mode:
                maybe_expr = [ASTLiteral(self.consume_char())]
            else:
                maybe_expr = None  # No operand for simple BSItems

        if maybe_expr is not None:
            return ASTFunction(function, maybe_expr)
        else:
            return ASTSymbol(function)


@dataclass
class ASTSymbol(ASTNode):
    name: str

    def convert(self) -> str:
        assert self.name in latex_charlist, "Unsupported symbol"
        basechar = latex_charlist[self.name]

        return ASTLiteral(basechar).convert()


@dataclass
class ASTFunction(ASTNode):
    name: str
    operands: list[ASTNode]

    def convert(self) -> str:
        operand = "".join(x.convert() for x in self.operands)
        current_context = font_context_stack[-1]
        new_context = copy.copy(current_context)

        if self.name == "^":
            new_context.is_superscript = True

        elif self.name == "_":
            new_context.is_subscript = True

        elif self.name == "vec":
            return operand + u'\u20d7'

        # TODO: More scalable approach to fixing conflicts
        elif self.name == "mathbb":
            new_context.is_double_struck = True
            new_context.is_italic = False  # Italic doublestruck variants don't exist
            new_context.is_bold = False  # Bold doublestruck variants don't exist

        elif self.name == "mathcal":
            new_context.is_script = True
            new_context.is_italic = False  # Italic script variants don't exist

        elif self.name == "mathfrak":
            new_context.is_fraktur = True
            new_context.is_italic = False  # Italic Fraktur variants don't exist

        # HACK: Shorthands
        elif self.name == "b":
            new_context.is_bold = True
            new_context.is_double_struck = False  # Bold doublestruck doesn't exist

        elif self.name == "i":
            new_context.is_italic = True
            new_context.is_fraktur = False  # Italic Fraktur doesn't exist
            new_context.is_script = False  # Italic script doesn't exist
            new_context.is_double_struck = False  # Bold doublestruck doesn't exist

        elif self.name == "bi" or self.name == "ib":
            new_context.is_bold = True
            new_context.is_italic = True
            new_context.is_double_struck = False  # Bold doublestruck doesn't exist
            new_context.is_fraktur = False  # Italic Fraktur doesn't exist
            new_context.is_script = False  # Italic script doesn't exist

        else:
            assert False, "Function not implemented"

        font_context_stack.append(new_context)
        # TODO: Find alternative to running this twice
        new_operand = "".join(x.convert() for x in self.operands)
        font_context_stack.pop()

        return new_operand


latex_charlist = {
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
