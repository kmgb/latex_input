import copy
from dataclasses import dataclass
import re

from latex_input.unicode_data import (
    superscript_mapping, subscript_mapping, character_font_variants, latex_symbols
)


@dataclass
class FontContext:
    is_bold: bool = False
    is_double_struck: bool = False
    is_fraktur: bool = False
    is_italic: bool = False
    is_monospace: bool = False
    is_sans_serif: bool = False
    is_script: bool = False
    is_subscript: bool = False
    is_superscript: bool = False

    def is_trivial(self) -> bool:
        return not (self.is_bold or self.is_double_struck or
                    self.is_fraktur or self.is_italic or
                    self.is_monospace or
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


def intersperse_characters(subject: str, intersperse: str) -> str:
    return "".join([x + intersperse for x in subject])


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
                and x.is_monospace == context.is_monospace
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
        # text = text.replace("/", "\u2044")

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
        assert self.name in latex_symbols, "Unsupported symbol"
        basechar = latex_symbols[self.name]

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
            new_context = FontContext(is_superscript=True)

        elif self.name == "_":
            new_context = FontContext(is_subscript=True)

        elif self.name == "vec":
            return operand + u'\u20d7'

        elif self.name == "sqrt":
            return "√" + intersperse_characters(operand, "\u0305")

        # TODO: Properly support \sqrt[\phi]{...}
        elif m := re.match(r"sqrt\[(.*)\]", self.name):
            param = m.group(1)
            symbol = "√"
            prefix = ""

            if param == "3":
                symbol = "∛"
            elif param == "4":
                symbol = "∜"
            else:
                prefix = to_superscript_form(param)

            return prefix + symbol + intersperse_characters(operand, "\u0305")

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

        elif self.name == "s":
            new_context = FontContext(is_sans_serif=True)

        elif self.name == "m":
            new_context = FontContext(is_monospace=True)

        # HACK: Shorthands
        elif all(c in "ibs" for c in self.name):
            if "b" in self.name:
                new_context.is_bold = True
                new_context.is_double_struck = False  # Bold doublestruck doesn't exist

            if "i" in self.name:
                new_context.is_italic = True
                new_context.is_fraktur = False  # Italic Fraktur doesn't exist
                new_context.is_script = False  # Italic script doesn't exist
                new_context.is_double_struck = False  # Italic doublestruck doesn't exist

            if "s" in self.name:
                new_context.is_sans_serif = True
                new_context.is_fraktur = False
                new_context.is_script = False
                new_context.is_double_struck = False

        else:
            assert False, "Function not implemented"

        font_context_stack.append(new_context)
        # TODO: Find alternative to running this twice
        new_operand = "".join(x.convert() for x in self.operands)
        font_context_stack.pop()

        return new_operand
