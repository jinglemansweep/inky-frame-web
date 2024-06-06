from pathlib import Path
from typing import List


class OutputDisplay:
    def __init__(
        self,
        image_files: List[Path],
        overlay_x: int,
        overlay_y: int,
        overlay_size: int,
        overlay_format: str,
        overlay_color: str,
    ) -> None:
        self.image_files = image_files
        self.image_count = len(image_files)
        self.image_index = 0
        self.image_iter = 0
        self.image_current = image_files[self.image_index]
        self.overlay_x = overlay_x
        self.overlay_y = overlay_y
        self.overlay_size = overlay_size
        self.overlay_format = overlay_format
        self.overlay_color = overlay_color

    def next(self) -> None:
        self.image_index = (self.image_index + 1) % self.image_count
        self.image_iter += 1

    @property
    def image_file(self) -> Path:
        return self.image_files[self.image_index]

    def __repr__(self) -> str:
        return (
            "<OutputDisplay items="
            + str(len(self.image_files))
            + " index="
            + str(self.image_index)
            + " image_iter="
            + str(self.image_iter)
            + " overlay_x="
            + str(self.overlay_x)
            + " overlay_y="
            + str(self.overlay_y)
            + " overlay_size="
            + str(self.overlay_size)
            + " overlay_format="
            + self.overlay_format
            + " overlay_color="
            + self.overlay_color
            + ">"
        )
