import datetime
from pathlib import Path


class Media:
    def __init__(self, media_path: Path, date_str: str) -> None:
        self.path: str = str(media_path)
        self.type: str = media_path.suffix
        self.date_str: str = date_str
        self.date: datetime.date = self._get_date(date_str)

    def _get_date(self, date_str: str) -> datetime.date:
        tmp = datetime.datetime.strptime(date_str, "%Y%m%d")
        return datetime.date(tmp.year, tmp.month, tmp.day)
