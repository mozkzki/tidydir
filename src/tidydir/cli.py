import os
import argparse
import logging
from pathlib import Path
from tidydir.core import organize


def run():
    parser = argparse.ArgumentParser(
        description="""
    画像や動画ファイルを日付フォルダに整理します
    """
    )

    parser.add_argument("target_dir", help="対象ディレクトリ")
    parser.add_argument("-d", "--debug", help="デバッグログ出力をONにします", action="store_true")

    args = parser.parse_args()

    # log設定
    formatter = "%(asctime)s %(levelname)-7s %(message)s"
    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    log_path = Path(os.getcwd(), "tidydir.log")
    logging.basicConfig(level=log_level, format=formatter, filename=log_path)

    # メインの処理
    print("")
    organize(target_dir=args.target_dir)
