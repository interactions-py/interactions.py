from typing import Optional, List

class LibraryException(Exception):
    message: Optional[str]
    code: Optional[int]
    severity: Optional[int]

    @staticmethod
    def _parse(_data: dict) -> List[tuple]: ...

    def log(self, message: str, *args) -> None: ...

    @staticmethod
    def lookup(code: int) -> str: ...
