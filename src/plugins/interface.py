from typing import Protocol, List, runtime_checkable

@runtime_checkable
class PluginProtocol(Protocol):
    """Basic plugin protocol for adapter shims.

    Implementations should provide a `name` and `description` attribute and
    a `run(args: List[str]) -> int` method. `run` should return an exit code.
    """

    name: str
    description: str

    def run(self, args: List[str]) -> int:...
