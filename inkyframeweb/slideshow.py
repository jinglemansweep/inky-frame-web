from datetime import datetime
from pathlib import Path
from typing import List


class Slideshow:
    def __init__(self, image_files: List[Path], delay_time: int = 60) -> None:
        self.delay_time = delay_time
        self.image_files = image_files
        self.image_count = len(image_files)
        self.image_index = 0
        self.image_current = image_files[self.image_index]
        self.start_time = int(datetime.now().timestamp())
        self.previous_time = self.start_time

    def should_advance(self, now: int) -> bool:
        advance = False
        diff = now - self.start_time
        if (diff % self.delay_time) == 0:
            if now != self.previous_time:
                self.previous_time = now
                advance = True
        return advance

    def next(self) -> None:
        self.image_index = (self.image_index + 1) % self.image_count

    @property
    def image_file(self) -> Path:
        return self.image_files[self.image_index]
