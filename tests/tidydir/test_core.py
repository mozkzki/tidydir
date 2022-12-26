import pytest
import os
import shutil
from tidydir.core import organize, _get_path


class TestCore:
    def test_organize(self):
        # -------------------
        # 実行前
        # -------------------
        # tests/data-org
        # ├── IMG_2031.jpg
        # ├── IMG_2031a.jpg
        # ├── IMG_2031b.jpg
        # ├── IMG_2031b.HEIC  ※対象外の拡張子なので移動されない
        # ├── exifcleaner-for-mac-Hero.jpeg  ※Exifが無いので移動されない
        # └── sub
        #      └── IMG_2031.mov  ※サブディレクトリは移動されない
        #
        # ↓
        #
        # -------------------
        # 実行後
        # -------------------
        # tests/data-tmp
        # └── 20220821
        #      ├── 2022-08-21_10-13-58.jpg
        #      ├── 2022-08-21_10-13-58-01.jpg  ※撮影日時が同じファイルは別名で保存
        #      └── 2022-08-21_10-13-58-02.jpg  ※撮影日時が同じファイルは別名で保存

        if os.path.exists("tidydir.db"):
            os.remove("tidydir.db")
        if os.path.exists("./tests/data-tmp"):
            shutil.rmtree("./tests/data-tmp")
        os.mkdir("./tests/data-tmp")

        organize("./tests/data-org", "./tests/data-tmp")

        file_count = sum(
            os.path.isfile(os.path.join("./tests/data-tmp/20220821", name))
            for name in os.listdir("./tests/data-tmp/20220821")
        )
        assert file_count == 3

        assert os.path.exists("./tests/data-tmp/20220821/2022-08-21_10-13-58.jpg") is True
        assert os.path.exists("./tests/data-tmp/20220821/2022-08-21_10-13-58-01.jpg") is True
        assert os.path.exists("./tests/data-tmp/20220821/2022-08-21_10-13-58-02.jpg") is True

    def test_get_path_error1(self):
        with pytest.raises(FileNotFoundError):
            _get_path("./tests/hoge")

    def test_get_path_error2(self):
        with pytest.raises(Exception):
            _get_path("./tests/core_test.py")
