
class PlumRuntimeError(RuntimeError):
    """A runtime error raised while executing a Plum program."""

    def __init__(self, message: str, node=None):
        self.message = message
        self.line = getattr(node, "line", None)
        self.column = getattr(node, "column", None)

        if self.line is not None and self.column is not None:
            formatted = (
                f"Runtime Error: {message}\n"
                f"  at line {self.line}, column {self.column}"
            )
        else:
            formatted = f"Runtime Error: {message}"

        super().__init__(formatted)


class PlumNameError(NameError):
    """A name-resolution error raised by a Plum program."""

    def __init__(self, message: str, node=None):
        self.message = message
        self.line = getattr(node, "line", None)
        self.column = getattr(node, "column", None)

        if self.line is not None and self.column is not None:
            formatted = (
                f"Runtime Error: {message}\n"
                f"  at line {self.line}, column {self.column}"
            )
        else:
            formatted = f"Runtime Error: {message}"

        super().__init__(formatted)
