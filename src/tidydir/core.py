import os
import json
import shutil
import logging
import requests
import sqlite3
from typing import List, Dict, Tuple
from pathlib import Path
from tidydir.define import TARGET_EXTENSIONS
from tidydir.media import Media
from dotenv import load_dotenv

dotenv_path = Path(os.getcwd(), ".env")
if dotenv_path.exists():
    load_dotenv(verbose=True, dotenv_path=dotenv_path)

# 固定値


SLACK_POST_URL = os.environ.get("slack_post_url", None)
SLACK_CHANNEL = os.environ.get("slack_post_channel", None)
LINE_POST_URL = os.environ.get("line_post_url", None)
DB_NAME = "tidydir.db"


def organize(target_dir: str = ".", out_dir: str = ".") -> None:
    # DB初期化
    _init_db()
    # 対象ディレクトリのPathオブジェクト
    target_path = _get_path(target_dir)
    # 対象ファイル取得
    medias: List[Media] = __get_medias(target_path)
    # コピー&移動
    out_path = _get_path(out_dir)
    move_result_simple, is_no_move = __copy_and_move(medias, out_path)
    if not is_no_move:
        print(move_result_simple)

        # Line通知
        __post_line_message(move_result_simple, target_path)
        # Slack通知
        __post_slack_message(move_result_simple, target_path)


def _get_path(target_dir: str = ".") -> Path:
    p = Path(target_dir)
    p = p.resolve()

    # 各種チェック
    if not p.exists():
        logging.warning("dir is not exist. path={}".format(str(p)))
        raise FileNotFoundError()
    if not p.is_dir():
        logging.warning("dir is not directory. path={}".format(str(p)))
        raise Exception("not directory")

    return p


def _rename_file(target_file: str, new_file_name: str, new_file_ext: str) -> Path:
    p = Path(target_file)
    p = p.resolve()
    if not p.exists():
        logging.warning("target file is not exist. path={}".format(str(p)))

    parent_dir = p.parent
    new_file = parent_dir.joinpath(new_file_name + new_file_ext)
    # 同じファイル名が既存ならリネームして継続
    if new_file.exists():
        # logging.warning("already exist!!!!!!!!!!! path={}".format(str(new_file)))
        i = 1
        while True:
            new_name = "{}-{:0=2}{}".format(new_file_name, i, new_file_ext)
            new_file = parent_dir.joinpath(new_name)
            if not new_file.exists():
                break
            i += 1
    return p.rename(new_file)


# 既存登録管理用のDBを初期化する
def _init_db():
    dbname = DB_NAME
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    for row in cur.execute("SELECT * FROM sqlite_master WHERE TYPE='table' AND name='medias'"):
        # すでに存在する場合
        conn.commit()
        conn.close()
        return
    cur.execute("CREATE TABLE medias(id INTEGER PRIMARY KEY AUTOINCREMENT, path STRING)")
    conn.commit()
    conn.close()


def _is_registered(media_path: Path) -> bool:
    dbname = DB_NAME
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    for row in cur.execute("SELECT id, path FROM medias WHERE path='" + str(media_path) + "'"):
        # print(row)
        cur.close()
        conn.close()
        return True
    cur.close()
    conn.close()
    return False


def _regist_media(media_path: Path):
    dbname = DB_NAME
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute('INSERT INTO medias(path) values("' + str(media_path) + '")')
    conn.commit()
    cur.close()
    conn.close()


def __get_medias(target_path: Path) -> List[Media]:
    # 対象拡張子のファイルパス(Pathオブジェクト)を取得
    logging.info("get media files from [{}]".format(str(target_path)))
    logging.info("target extensions: {}".format(TARGET_EXTENSIONS))
    media_paths = []
    for ext in TARGET_EXTENSIONS:
        media_paths.extend(list(target_path.glob("*" + ext)))  # "**/*.mov"とするとサブディレクトリも検索

    # Mediaオブジェクトに変換
    medias = []
    for media_path in media_paths:
        # 処理済みならスキップ
        if _is_registered(media_path):
            continue

        media = Media(media_path)
        if media.date_str != "":
            # logging.info("found. [{}]".format(str(media_path)))
            medias.append(media)
        else:
            logging.warning("found no metadata media. [{}]".format(str(media_path)))
            media.date_str = "撮影日不明"
            medias.append(media)

        # 処理済みとして登録
        _regist_media(media_path)

        # pattern = re.compile(r"(\d{4}-\d{2}-\d{2}) \d{2}\.\d{2}\.\d{2}\.*")
        # m = pattern.search(str(media_path))
        # if m:
        #     # フォーマットに一致したもののみ対象とする
        #     date_str = m.groups()[0].replace("-", "")
        #     logging.info("found. [{}]".format(str(media_path)))
        #     medias.append(Media(media_path, date_str))

    if len(medias) > 0:
        logging.info("{} target files found.".format(len(medias)))
    else:
        logging.info("no target files found.")

    return medias


def __copy_and_move(medias: List[Media], target_path: Path) -> Tuple[str, bool]:
    move_result_simple: str = ""

    sorted_medias = sorted(medias, key=lambda x: x.date)
    date_group_medias: Dict[str, List[Media]] = {}
    for media in sorted_medias:
        if date_group_medias.get(media.date_str, None) is None:
            date_group_medias[media.date_str] = []
        date_group_medias[media.date_str].append(media)

    all_count = 0
    for key in date_group_medias:
        # 日付フォルダ作成
        date_dir: Path = target_path.joinpath(key.replace("/", ""))
        date_dir.mkdir(exist_ok=True)

        media_list = date_group_medias[key]
        count = 0
        for media in media_list:
            # ファイルを日付フォルダにコピー
            new_path_str = shutil.copy(media.path, str(date_dir))
            # 撮影日不明の場合はリネームしない
            if media.date_str != "撮影日不明":
                new_path = _rename_file(new_path_str, media.datetime_str, media.type)
            else:
                new_path = Path(new_path_str)
            logging.info(
                "  [{}] copy! ({}) {} -> {}".format(key, media.type, media.path, str(new_path))
            )
            count += 1

        logging.info("  [{}] count: {}".format(key, count))
        result_tmp = "{} (count: {})\n".format(key, count)
        move_result_simple += result_tmp
        all_count += count

    logging.info("{} files copied.".format(all_count))
    move_result_simple = "{} files copied.\n{}".format(all_count, move_result_simple)
    is_no_move = True if all_count == 0 else False

    return move_result_simple, is_no_move


def __post_line_message(message: str, target_path: Path) -> None:
    if LINE_POST_URL is None:
        logging.warning("can't post message to LINE. because LINE url is null.")
        return

    if message == "":
        logging.info("omit post message to LINE. because message is empty.")
        return

    message = "写真と動画を整理しました。\n({})\n\n".format(target_path.name) + message
    line_message = {
        "message": message,
    }
    try:
        requests.post(LINE_POST_URL, data=json.dumps(line_message))
        logging.info("line message posted.")
    except requests.exceptions.RequestException as e:
        logging.error("request failed: {}".format(e))


def __post_slack_message(message: str, target_path: Path) -> None:
    if SLACK_POST_URL is None:
        logging.warning("can't post message to slack. because slack url is null.")
        return

    if message == "":
        logging.info("omit post message to slack. because message is empty.")
        return

    message = "写真と動画を整理しました。\n({})\n\n".format(target_path.name) + message
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
