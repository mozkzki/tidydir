import pytest
import os
import shutil
from tidydir.core import organize, _get_path


class TestCore:
    def test_organize(self):
        # -------------------
        # 実行前
        # -------------------
        # tests/data
        # ├── 2020-01-01\ 10.10.10.jpg
        # ├── 2020-05-05\ 12.12.12.mov
        # ├── abcde.mov
        # └── sub
        #      ├── 2020-06-06\ 12.12.12.mov
        #      └── abcde.mov
        #
        # ↓
        #
        # -------------------
        # 実行後
        # -------------------
        # tests/data
        # ├── 20200101
        # │   └── 2020-01-01\ 10.10.10.jpg
        # ├── 20200505
        # │   └── 2020-05-05\ 12.12.12.mov
        # ├── abcde.mov                      ※ ファイル名が日付形式を満たさないので移動されない
        # └── sub
        #      ├── 2020-06-06\ 12.12.12.mov  ※ 再帰的に検索しないので移動されない
        #      └── abcde.mov                 ※ 再帰的に検索しないので移動されない

        organize("./tests/data")
        assert os.path.exists("./tests/data/20200101/2020-01-01 10.10.10.jpg") is True
        assert os.path.exists("./tests/data/20200505/2020-05-05 12.12.12.mov") is True
        assert os.path.exists("./tests/data/20200606/2020-06-06 12.12.12.mov") is False
        assert os.path.exists("./tests/data/abcde.mov") is True
        assert os.path.exists("./tests/data/sub/2020-06-06 12.12.12.mov") is True
        assert os.path.exists("./tests/data/sub/abcde.mov") is True

        # テスト前の状態に戻す
        shutil.move("./tests/data/20200101/2020-01-01 10.10.10.jpg", "./tests/data/")
        shutil.move("./tests/data/20200505/2020-05-05 12.12.12.mov", "./tests/data/")
        shutil.rmtree("./tests/data/20200101")
        shutil.rmtree("./tests/data/20200505")

    def test_get_path_error1(self):
        with pytest.raises(FileNotFoundError):
            _get_path("./tests/hoge")

    def test_get_path_error2(self):
        with pytest.raises(Exception):
            _get_path("./tests/core_test.py")
