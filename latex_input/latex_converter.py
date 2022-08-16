import re

from latex_input.parse_unicode_data import superscript_mapping, subscript_mapping

def latex_to_unicode(tex) -> str:
    parser = LatexRDescentParser()
    return parser.parse(tex)

def to_superscript_form(t:str) -> str:
    return "".join([superscript_mapping[c][0] for c in t])

def to_subscript_form(t:str) -> str:
    return "".join([subscript_mapping[c][0] for c in t])

r"""
Recursive descent parser that employs the following grammar rules:
latex -> expr*
expr  -> ε | text | macro
macro -> \(text|^|_){expr}
text  -> [a-zA-Z0-9]+
"""
class LatexRDescentParser:
    expression = ""
    index = 0
    output = ""

    def parse(self, expression) -> str:
        self.expression = expression

        while self.index < len(self.expression) - 1:
            self.output += self._expr()

        return self.output

    def consume(self, expr) -> str:
        m = re.match(expr, self.expression[self.index:])
        print(m)
        assert m

        self.index += m.end()

        print(f"ATE {m.group()}")

        return m.group()

    def _expr(self) -> str:
        if self.index >= len(self.expression) - 1:
            return ""

        if self.expression[self.index] in ["\\", "^", "_"]:
            return self._macro()

        return self._text()

    def _macro(self) -> str:
        op = self.consume(r"[\\^_]")

        if op == "\\":
            op = self._text()

        self.consume("{")

        expr = self._expr()

        self.consume("}")

        if op == "^":
            return to_superscript_form(expr)
        elif op == "_":
            return to_subscript_form(expr)
        elif op == "vec":
            return expr + u'\u20d7'
        else:
            assert False, "Unsupported macro"

    def _text(self) -> str:
        return self.consume("[a-zA-Z0-9]+")
