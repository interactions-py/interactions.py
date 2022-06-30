from typing import Optional, List

class LibraryException(Exception):
    message: Optional[str]
    code: Optional[int]
    severity: Optional[int]
    data: Optional[dict]

    def __init__(self, code: int = 0, message: str = None, severity: int = 0, **kwargs): ...
    @staticmethod
    def _parse(_data: dict) -> List[tuple]: ...
    def log(self, message: str, *args) -> None: ...
    @staticmethod
    def lookup(code: int) -> str: ...
