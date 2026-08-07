from dataclasses import dataclass
from .token_type import TokenType

@dataclass
class Token:
    type: TokenType
    value: str
    line: int

    def __repr__(self) -> str:
        return (
            f"Token("
            f"type={self.type.name}, "
            f"value={self.value!r}, "
            f"line={self.line})"
        )