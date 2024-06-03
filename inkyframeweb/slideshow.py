from datetime import datetime
from pathlib import Path
from typing import List


class Slideshow:
    def __init__(
        self,
        image_files: List[Path],
        image_size: tuple[int, int],
        delay: int = 60,
        show_date: bool = True,
        show_time: bool = True,
        show_watermark: bool = False,
    ) -> None:
        self.delay = delay
        self.image_files = image_files
        self.image_count = len(image_files)
        self.image_index = 0
        self.image_current = image_files[self.image_index]
        self.start_time = int(datetime.now().timestamp())
        self.previous_time = self.start_time
        self.image_size = image_size
        self.show_date = show_date
        self.show_time = show_time
        self.show_watermark = show_watermark

    def should_advance(self, now: int) -> bool:
        advance = False
        diff = now - self.start_time
        if (diff % self.delay) == 0:
            if now != self.previous_time:
                self.previous_time = now
                advance = True
        return advance

    def next(self) -> None:
        self.image_index = (self.image_index + 1) % self.image_count

    @property
    def image_file(self) -> Path:
        return self.image_files[self.image_index]
