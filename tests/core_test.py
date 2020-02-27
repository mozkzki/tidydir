import pytest
import shutil
from mediafileorganizer.core import organize, _get_path


class TestCore:
    def test_organize(self):
        organize("./tests/data")
        # 戻す
        shutil.move("./tests/data/20200101/2020-01-01 10.10.10.jpg", "./tests/data/")
        shutil.move("./tests/data/20200505/2020-05-05 12.12.12.mov", "./tests/data/")

    def test_get_path_error1(self):
        with pytest.raises(FileNotFoundError):
            _get_path("./tests/hoge")

    def test_get_path_error2(self):
        with pytest.raises(Exception):
            _get_path("./tests/core_test.py")
