from dataclasses import dataclass

@dataclass
class FileChange:
    filename: str
    added_lines: list[str]
    removed_lines: list[str]
    hunks: list[str]
    change_summary: str
