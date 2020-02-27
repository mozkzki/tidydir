import argparse
import logging
from mediafileorganizer.core import organize


def main():
    parser = argparse.ArgumentParser(
        description="""
    画像や動画ファイルを日付フォルダに整理します
    """
    )

    parser.add_argument("target_dir", help="対象ディレクトリ")
    parser.add_argument("-f", "--logfile", help="ログを出力するファイルパスを指定します")
    parser.add_argument("-d", "--debug", help="デバッグログ出力をONにします", action="store_true")
    parser.add_argument("-l", "--line", help="LINE通知を有効にします", action="store_true")

    args = parser.parse_args()

    # log設定
    formatter = "%(asctime)s %(levelname)-7s %(message)s"
    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level, format=formatter)
    # logging.basicConfig(level=log_level, format=formatter, filename="hoge.log")

    # メインの処理
    print("")
    organize(target_dir=args.target_dir, post_line=args.line)


if __name__ == "__main__":
    main()
