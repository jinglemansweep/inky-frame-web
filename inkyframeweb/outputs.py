from pathlib import Path
from typing import List


class OutputDisplay:
    def __init__(
        self,
        image_files: List[Path],
        show_date: bool = True,
        show_time: bool = True,
    ) -> None:
        self.image_files = image_files
        self.image_count = len(image_files)
        self.image_index = 0
        self.image_current = image_files[self.image_index]
        self.show_date = show_date
        self.show_time = show_time

    def next(self) -> None:
        self.image_index = (self.image_index + 1) % self.image_count

    @property
    def image_file(self) -> Path:
        return self.image_files[self.image_index]

    def __repr__(self) -> str:
        return (
            "<OutputDisplay items="
            + str(len(self.image_files))
            + " show_date="
            + str(self.show_date)
            + " show_time="
            + str(self.show_time)
            + ">"
        )
