from dataclasses import dataclass
from .token_type import TokenType


@dataclass
class Token:
    type: TokenType
    value: object
    line: int
    column: int = 1

    def __repr__(self) -> str:
        return (
            f"Token("
            f"type={self.type.name}, "
            f"value={self.value!r}, "
            f"line={self.line}, "
            f"column={self.column})"
        )