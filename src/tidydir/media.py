import datetime
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS


class Media:
    def __init__(self, media_path: Path) -> None:
        self.path: str = str(media_path)
        self.type: str = media_path.suffix
        self.exif_shooting_datetime: str = self._get_exif_shooting_datetime_str(
            media_path
        )
        self.date_str: str = self._get_date_str(media_path)
        self.datetime_str: str = self._get_datetime_str(media_path)
        self.date: datetime.date = self._get_date(media_path)
        self.datetime: datetime.datetime = self._get_datetime(media_path)

    def _get_exif_shooting_datetime_str(self, media_path: Path) -> str:
        exif = self.__get_exif(media_path)
        return exif.get(306, "")  # 306 == DateTime

    def _get_date_str(self, media_path: Path) -> str:
        date_time_str = self._get_exif_shooting_datetime_str(media_path)
        date_str: str = date_time_str.split(" ")[0].replace(":", "")
        return date_str

    def _get_datetime_str(self, media_path: Path) -> str:
        datetime_str: str = self._get_exif_shooting_datetime_str(media_path)
        datetime_str = datetime_str.replace(" ", "_")
        datetime_str = datetime_str.replace(":", "-")
        return datetime_str

    def _get_date(self, media_path: Path) -> datetime.date:
        date_time_str = self._get_exif_shooting_datetime_str(media_path)
        if date_time_str == "":
            return datetime.date.min
        tmp = datetime.datetime.strptime(date_time_str, "%Y:%m:%d %H:%M:%S")
        return datetime.date(tmp.year, tmp.month, tmp.day)

    def _get_datetime(self, media_path: Path) -> datetime.datetime:
        date_time_str = self._get_exif_shooting_datetime_str(media_path)
        if date_time_str == "":
            return datetime.datetime.min
        tmp = datetime.datetime.strptime(date_time_str, "%Y:%m:%d %H:%M:%S")
        return datetime.datetime(
            tmp.year, tmp.month, tmp.day, tmp.hour, tmp.minute, tmp.second
        )

    def __get_exif(self, media_path: Path):
        with Image.open(media_path) as im:
            exif = im.getexif()
            # self.__print_exif_items(exif)
            return exif

    def __print_exif_items(self, exif):
        for k, v in exif.items():
            print(f"{k}: {TAGS.get(k, k)}: {v}")
