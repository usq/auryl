class AurylError(Exception):
    ...

class TypeNotFoundError(AurylError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Cannot find type '{name}'")
