from dataclasses import dataclass


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
        return self.text
