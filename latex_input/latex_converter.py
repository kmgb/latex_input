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

        if context.is_trivial():
            return self.text

        if context.is_superscript:
            return to_superscript_form(self.text)

        elif context.is_subscript:
            return to_subscript_form(self.text)

        output = ""
        for basechar in self.text:
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
    char_regex = re.compile(r"(?:[a-zA-Z0-9 =\!]|(?:\\[\\\^_\{}]))")
    text_regex = re.compile(r"(?:[a-zA-Z0-9 =\!]|(?:\\[\\\^_\{}]))+")

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
