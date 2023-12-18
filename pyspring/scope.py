import enum


class Scope(enum.Enum):
    singleton = "singleton"
    prototype = "prototype"

    @staticmethod
    def from_string(scope: str) -> "Scope":
        for item in Scope.__members__.values():
            if item.value == scope:
                return item
        raise ValueError(f"Scope {scope} is not supported")
