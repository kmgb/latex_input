from dataclasses import dataclass
import re

from latex_input.parse_unicode_data import (
    superscript_mapping, subscript_mapping, mathbb_mapping, mathcal_mapping, mathfrak_mapping
)


def latex_to_unicode(tex) -> str:
    parser = LatexRDescentParser()

    try:
        result = parser.parse(tex)
        print(result)
        return result.convert()
    except Exception as e:
        print(f"Failed to convert {tex}")
        return "ERROR"


def _map_text(mapping: dict[str, str], text: str) -> str:
    # Iterate all characters in text and convert them using map
    return "".join([mapping[c] for c in text])


def to_superscript_form(t: str) -> str:
    return _map_text(superscript_mapping, t)


def to_subscript_form(t: str) -> str:
    return _map_text(subscript_mapping, t)


def to_mathbb_form(t: str) -> str:
    return _map_text(mathbb_mapping, t)


def to_mathcal_form(t: str) -> str:
    return _map_text(mathcal_mapping, t)


def to_mathfrak_form(t: str) -> str:
    return _map_text(mathfrak_mapping, t)


@dataclass
class ASTNode:
    def convert(self) -> str:
        assert False, "Not implemented"


@dataclass
class ASTLaTeX(ASTNode):
    nodes: list[ASTNode]

    def convert(self) -> str:
        return "".join(n.convert() for n in self.nodes)


class LatexRDescentParser:
    r"""
    Recursive descent parser that employs the following grammar rules:
    LaTeX   -> Expr*
    Expr    -> ε | Text | BSItem | Macro
    Macro   -> (\Text|^|_){Expr} | ^Char | _Char
    BSItem  -> \Text
    Text    -> Char+
    Char    -> [a-zA-Z0-9 ]
    """
    expression = ""
    index = 0
    char_regex = "[a-zA-Z0-9 ]"
    text_regex = char_regex + "+"

    def parse(self, expression) -> ASTNode:
        self.expression = expression
        self.index = 0
        nodes = []

        while self.index < len(self.expression):
            nodes.append(self._expr())

        return ASTLaTeX(nodes)

    def consume(self, expr) -> str:
        m = re.match(expr, self.expression[self.index:])
        assert m

        self.index += m.end()

        # print(f"ATE {m.group()}")

        return m.group()

    def peek(self) -> str:
        if self.index >= len(self.expression):
            return ""

        return self.expression[self.index]

    def _expr(self) -> ASTNode:
        if self.index >= len(self.expression):
            return ASTLiteral("")

        if self.peek() in ["\\", "^", "_"]:
            return self._macro()

        return ASTLiteral(self._text())

    def _macro(self) -> ASTNode:
        function = self.consume(r"[\\^_]")

        single_char_mode = False

        if function == "\\":
            function = self._text()

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
                maybe_expr = [ASTLiteral(self._char())]
            else:
                maybe_expr = None  # No operand for simple BSItems

        if maybe_expr is not None:
            return ASTFunction(function, maybe_expr)
        else:
            return ASTSymbol(function)

        # if function == "^":
        #     return to_superscript_form(expr)
        # elif function == "_":
        #     return to_subscript_form(expr)
        # elif expr:
        #     return self.handle_macro(function, expr)
        # else:
        #     return self.handle_bsitem(function)

    def handle_macro(self, name: str, operand: str) -> str:
        if name == "vec":
            return operand + u'\u20d7'

        if name == "mathbb":
            return to_mathbb_form(operand)

        if name == "mathcal":
            return to_mathcal_form(operand)

        if name == "mathfrak":
            return to_mathfrak_form(operand)

        assert False, "Unsupported macro"

    def handle_bsitem(self, name: str) -> str:
        if name in latex_charlist:
            return latex_charlist[name]

        assert False, "Unsupported bsitem"

    def _text(self) -> str:
        return self.consume(self.text_regex)

    def _char(self) -> str:
        return self.consume(self.char_regex)


@dataclass
class ASTLiteral(ASTNode):
    text: str

    def convert(self) -> str:
        return self.text


@dataclass
class ASTSymbol(ASTNode):
    name: str

    def convert(self) -> str:
        return latex_charlist.get(self.name) or "INVALID SYMBOL"


@dataclass
class ASTFunction(ASTNode):
    name: str
    operands: list[ASTNode]

    def convert(self) -> str:
        assert len(self.operands) == 1

        operand = "".join(x.convert() for x in self.operands)

        if self.name == "^":
            return to_superscript_form(operand)

        elif self.name == "_":
            return to_subscript_form(operand)

        elif self.name == "vec":
            return operand + u'\u20d7'

        elif self.name == "mathbb":
            return to_mathbb_form(operand)

        elif self.name == "mathcal":
            return to_mathcal_form(operand)

        elif self.name == "mathfrak":
            return to_mathfrak_form(operand)

        else:
            assert False, "Function not implemented"


latex_charlist = {
    # Greek letters
    "Alpha":   u"\u0391",
    "Beta":    u"\u0392",
    "Gamma":   u"\u0393",
    "Delta":   u"\u0394",
    "Epsilon": u"\u0395",
    "Zeta":    u"\u0396",
    "Eta":     u"\u0397",
    "Theta":   u"\u0398",
    "Iota":    u"\u0399",
    "Kappa":   u"\u039A",
    "Lambda":  u"\u039B",
    "Mu":      u"\u039C",
    "Nu":      u"\u039D",
    "Xi":      u"\u039E",
    "Omicron": u"\u039F",
    "Pi":      u"\u03A0",
    "Rho":     u"\u03A1",
    "Sigma":   u"\u03A3",
    "Tau":     u"\u03A4",
    "Upsilon": u"\u03A5",
    "Phi":     u"\u03A6",
    "Chi":     u"\u03A7",
    "Psi":     u"\u03A8",
    "Omega":   u"\u03A9",
    "alpha":   u"\u03B1",
    "beta":    u"\u03B2",
    "gamma":   u"\u03B3",
    "delta":   u"\u03B4",
    "epsilon": u"\u03F5",  # NOTE: This is the lunate form by default. Varepsilon is the reversed-3
    "zeta":    u"\u03B6",
    "eta":     u"\u03B7",
    "theta":   u"\u03B8",
    "iota":    u"\u03B9",
    "kappa":   u"\u03BA",
    "lambda":  u"\u03BB",
    "mu":      u"\u03BC",
    "nu":      u"\u03BD",
    "xi":      u"\u03BE",
    "omicron": u"\u03BF",
    "pi":      u"\u03C0",
    "rho":     u"\u03C1",
    "sigma":   u"\u03C3",
    "tau":     u"\u03C4",
    "upsilon": u"\u03C5",
    "phi":     u"\u03D5",  # NOTE: This is the closed form by default. Varphi is the open form
    "chi":     u"\u03C7",
    "psi":     u"\u03C8",
    "omega":   u"\u03C9",

    # Greek letter variants
    "varepsilon":   u"\u03B5",  # ε
    "vartheta":     u"\u03D1",  # ϑ
    "varpi":        u"\u03D6",  # ϖ
    "varrho":       u"\u03F1",  # ϱ
    "varsigma":     u"\u03C2",  # ς
    "varphi":       u"\u03C6",  # φ

    # Math and logic
    "neg":         u"\u00AC",  # ¬ Negation
    "times":       u"\u00D7",  # × Multiplication / cross product
    "forall":      u"\u2200",  # ∀ Upside down capital A
    "partial":     u"\u2202",  # ∂ Partial derivative symbol
    "exists":      u"\u2203",  # ∃ Backwards capital E
    "empty":       u"\u2205",  # ∅ Empty set symbol
    "nabla":       u"\u2207",  # ∇ Vector differential
    "in":          u"\u2208",  # ∈ Element of
    "infty":       u"\u221E",  # ∞ Infinity symbol
    "land":        u"\u2227",  # ∧ Logical conjunction
    "lor":         u"\u2228",  # ∨ Logical disjunction
    "int":         u"\u222B",  # ∫ Integral
    "iint":        u"\u222C",  # ∬ Double integral
    "iiint":       u"\u222D",  # ∭ Triple integral
    "oint":        u"\u222E",  # ∮ Closed integral
    "oiint":       u"\u222F",  # ∯ Closed double integral
    "oiiint":      u"\u2230",  # ∰ Closed triple integral
    "therefore":   u"\u2234",  # ∴ Therefore symbol
    "because":     u"\u2235",  # ∵ Since symbol
    "approx":      u"\u2248",  # ≈ Approx equal
    "neq":         u"\u2260",  # ≠ Not equal
    "equiv":       u"\u2261",  # ≡ Equivalence operator
    "true":        u"\u22A4",  # ⊤ Truth symbol
    "false":       u"\u22A5",  # ⊥ Falsity symbol
    "models":      u"\u22A8",  # ⊨ Double turnstile
    "nmodels":     u"\u22AD",  # ⊭ Negated double turnstile
    "cdot":        u"\u22C5",  # ⋅ Dot product operator
    "implies":     u"\u27F9",  # ⟹ Implies arrow
    "iff":         u"\u27FA",  # ⟺ If and only if arrow
}
