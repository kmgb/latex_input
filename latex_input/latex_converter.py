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
macro -> \(text|^|_){expr} NOTE: Curly braces are optional for ^ and _, but only for one character
text  -> char+
char  -> [a-zA-Z0-9]
"""
class LatexRDescentParser:
    expression = ""
    index = 0
    output = ""

    def parse(self, expression) -> str:
        self.expression = expression

        while self.index < len(self.expression):
            self.output += self._expr()

        return self.output

    def consume(self, expr) -> str:
        m = re.match(expr, self.expression[self.index:])
        print(m)
        assert m

        self.index += m.end()

        print(f"ATE {m.group()}")

        return m.group()

    def peek(self) -> str:
        return self.expression[self.index]

    def _expr(self) -> str:
        if self.index >= len(self.expression):
            return ""

        if self.peek() in ["\\", "^", "_"]:
            return self._macro()

        return self._text()

    def _macro(self) -> str:
        op = self.consume(r"[\\^_]")

        needs_braces = False
        if op == "\\":
            op = self._text()
            needs_braces = True

        if needs_braces or self.peek() == "{":
            self.consume("{")

            expr = ""
            while self.peek() != "}":
                expr += self._expr()

            self.consume("}")
        else:
            expr = self._char()

        if op == "^":
            return to_superscript_form(expr)
        elif op == "_":
            return to_subscript_form(expr)
        elif op == "vec":
            return expr + u'\u20d7'
        else:
            assert False, "Unsupported macro"

    def _text(self) -> str:
        return self.consume("[a-zA-Z0-9 ]+")

    def _char(self) -> str:
        return self.consume("[a-zA-z0-9 ]")
