import datetime
import subprocess
import re

# import time
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
from tidydir.define import TARGET_EXTENSIONS_MOVIE


class Media:
    def __init__(self, media_path: Path) -> None:
        # iCloudの場合、openするまでファイル実体が保持されないため
        # ここで強制的にopen
        # f = open(str(media_path), "rb")
        # f.close()
        # それでもたまにエラーになるため・・
        # time.sleep(2)

        self.path: str = str(media_path)
        self.type: str = media_path.suffix

        shooting_datetime_str = self._get_shooting_datetime_str(media_path)
        self.exif_shooting_datetime: str = shooting_datetime_str

        self.date_str: str = self._get_date_str(shooting_datetime_str)
        self.datetime_str: str = self._get_datetime_str(shooting_datetime_str)
        self.date: datetime.date = self._get_date(shooting_datetime_str)
        self.datetime: datetime.datetime = self._get_datetime(shooting_datetime_str)

    def _get_shooting_datetime_str(self, media_path: Path) -> str:
        ext = media_path.suffix
        if ext not in TARGET_EXTENSIONS_MOVIE:
            # 動画ではない場合
            with Image.open(media_path) as im:
                exif = im.getexif()
                # self.__print_exif_items(exif)
                if exif is not None:
                    return exif.get(306, "")  # 306 == DateTime
                else:
                    return ""

        # 動画の場合
        return self.__get_movie_shooting_datetime_str(media_path)

    def _get_date_str(self, datetime_str: str) -> str:
        date_str: str = datetime_str.split(" ")[0].replace(":", "-")
        return date_str

    def _get_datetime_str(self, datetime_str: str) -> str:
        datetime_str = datetime_str.replace(" ", "_")
        datetime_str = datetime_str.replace(":", "-")
        return datetime_str

    def _get_date(self, datetime_str: str) -> datetime.date:
        if datetime_str == "":
            return datetime.date.min
        tmp = datetime.datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
        return datetime.date(tmp.year, tmp.month, tmp.day)

    def _get_datetime(self, datetime_str: str) -> datetime.datetime:
        if datetime_str == "":
            return datetime.datetime.min
        tmp = datetime.datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
        return datetime.datetime(
            tmp.year, tmp.month, tmp.day, tmp.hour, tmp.minute, tmp.second
        )

    def __get_movie_shooting_datetime_str(self, media_path: Path) -> str:
        path = str(media_path)
        # print('ffmpeg -i "' + path + '"')
        result = subprocess.run(
            'ffmpeg -i "' + path + '"',
            shell=True,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        # print(result.stderr)
        m = re.search("(?<=com.apple.quicktime.creationdate: )(.*)", result.stderr)
        if m is not None:
            datetime_str = m.group(1)
            datetime_str = datetime_str[:-5]
            datetime_str = datetime_str.replace("T", " ")
            datetime_str = datetime_str.replace("-", ":")
            return datetime_str

        # iOS以外は下記で取得
        m = re.search("creation_time +: (.*)", result.stderr)
        if m is not None:
            datetime_str = m.group(1)
            datetime_str = datetime_str[:-9]
            datetime_str = datetime_str.replace("T", " ")
            datetime_str = datetime_str.replace("-", ":")
            # 日本時間に直す (quicktime.creationdateは日本時間だが、こちらはGMT）
            tmp = datetime.datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
            tmp_datetime = datetime.datetime(
                tmp.year,
                tmp.month,
                tmp.day,
                tmp.hour,
                tmp.minute,
                tmp.second,
            )
            tmp_datetime = tmp_datetime + datetime.timedelta(hours=9)
            return tmp_datetime.strftime("%Y:%m:%d %H:%M:%S")

        return ""

    def __print_exif_items(self, exif):
        for k, v in exif.items():
            print(f"{k}: {TAGS.get(k, k)}: {v}")
