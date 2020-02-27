import os
import re
import json
import shutil
import logging
import requests
from typing import List, Dict, Tuple
from pathlib import Path
from mediafileorganizer.media import Media
from dotenv import load_dotenv

load_dotenv(verbose=True)

# 固定値
TARGET_EXTENSIONS = ["mov", "jpg"]
LOG_FILE = "mediafile-organizer.log"
HISTORY_FILE = "mediafile-organizer-history"
SLACK_POST_URL = os.environ["slack_post_url"]
SLACK_CHANNEL = os.environ["slack_post_channel"]
LINE_POST_URL = os.environ["line_post_url"]

# log設定
# formatter = "%(asctime)s %(levelname)-7s %(message)s"
# logging.basicConfig(level=logging.DEBUG, filename=LOG_FILE, format=formatter)


def organize(target_dir: str = ".", post_line: bool = True) -> None:
    # 対象ディレクトリのPathオブジェクト
    target_path = _get_path(target_dir)
    # 対象ファイル取得
    medias: List[Media] = _get_medias(target_path)
    # 移動
    move_result, move_result_simple = _move(medias, target_path)
    # 履歴に追記
    _append_history(move_result, target_path.name)
    # Line通知
    if post_line:
        _post_line_message(move_result_simple)
    # Slack通知
    _post_slack_message(move_result_simple)


def _get_path(target_dir: str = ".") -> Path:
    p = Path(target_dir)
    p = p.resolve()

    # 各種チェック
    if not p.exists():
        logging.warning("target dir is not exist. path={}".format(str(p)))
        raise FileNotFoundError()
    if not p.is_dir():
        logging.warning("target dir is not directory. path={}".format(str(p)))
        raise Exception("not directory")

    return p


def _get_medias(target_path: Path) -> List[Media]:
    # 対象拡張子のファイルパス(Pathオブジェクト)を取得
    logging.info("get media files from [{}]".format(str(target_path)))
    media_paths = []
    for ext in TARGET_EXTENSIONS:
        media_paths.extend(list(target_path.glob("*." + ext)))  # "**/*.mov"とするとサブディレクトリも検索

    # Mediaオブジェクトに変換
    medias = []
    for media_path in media_paths:
        pattern = re.compile(r"(\d{4}-\d{2}-\d{2}) \d{2}\.\d{2}\.\d{2}\.*")
        m = pattern.search(str(media_path))
        if m:
            # フォーマットに一致したもののみ対象とする
            date_str = m.groups()[0].replace("-", "")
            logging.info("found. [{}]".format(str(media_path)))
            medias.append(Media(media_path, date_str))

    if len(medias) > 0:
        logging.info("{} media files found.".format(len(medias)))
    else:
        logging.info("no media files found.")

    return medias


def _move(medias: List[Media], target_path: Path) -> Tuple[str, str]:
    # 移動の結果として下記のような文字列を返却
    # --------------------------------
    # 2020/01/07 (count: 2)
    #   [img] d:/path/of/image.jpg
    #   [mov] d:/path/of/movie.mov
    # --------------------------------
    move_result: str = ""
    move_result_simple: str = ""

    sorted_medias = sorted(medias, key=lambda x: x.date)
    date_group_medias: Dict[str, List[Media]] = {}
    for media in sorted_medias:
        if date_group_medias.get(media.date_str, None) is None:
            date_group_medias[media.date_str] = []
        date_group_medias[media.date_str].append(media)

    for key in date_group_medias:
        # 日付フォルダ作成
        date_dir: Path = target_path.joinpath(key.replace("/", ""))
        date_dir.mkdir(exist_ok=True)

        media_list = date_group_medias[key]
        result_line = ""
        count = 0
        for media in media_list:
            # ファイルを日付フォルダに移動
            new_path = shutil.move(media.path, str(date_dir))
            result_line += "  [{}] {} -> {}\n".format(media.type, media.path, new_path)
            count += 1

        result_tmp = "{} (count: {})\n".format(key, count)
        move_result += result_tmp + result_line
        move_result_simple += result_tmp

    return move_result, move_result_simple


def _append_history(history: str, target_dir_name: str) -> None:
    if history == "":
        return
    with open("{}-{}.log".format(HISTORY_FILE, target_dir_name), mode="a") as f:
        f.write("{}".format(history))


def _post_line_message(message: str) -> None:
    if message == "":
        return

    line_message = {
        "message": message,
    }
    try:
        requests.post(LINE_POST_URL, data=json.dumps(line_message))
        logging.info("line message posted.")
    except requests.exceptions.RequestException as e:
        logging.error("request failed: {}".format(e))


def _post_slack_message(message: str) -> None:
    if message == "":
        return

    slack_message = {
        "message": message,
        "color": "good",
        "channel": SLACK_CHANNEL,
    }
    try:
        requests.post(SLACK_POST_URL, data=json.dumps(slack_message))
        logging.info("slack message posted to {}.".format(slack_message["channel"]))
    except requests.exceptions.RequestException as e:
        logging.error("request failed: {}".format(e))
