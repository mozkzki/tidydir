# tidydir

[![CircleCI](https://circleci.com/gh/mozkzki/tidydir/tree/master.svg?style=svg)](https://circleci.com/gh/mozkzki/tidydir/tree/master)
[![codecov](https://codecov.io/gh/mozkzki/tidydir/branch/master/graph/badge.svg?token=BRB5vsPkO2)](https://codecov.io/gh/mozkzki/tidydir)
[![Maintainability](https://api.codeclimate.com/v1/badges/df50bbce59225073a577/maintainability)](https://codeclimate.com/github/mozkzki/tidydir/maintainability)

指定ディレクトリ内のファイルを日付フォルダに整理する。
スマホやカメラの画像/動画ファイルの日付整理を想定。

- 対象のファイル(拡張子)は下記の通り
```txt
    "jpg",
    "JPG",
    "jpeg",
    "JPEG",
    "png",
    "PNG",
    "mp4",
    "MP4",
    "mov",
    "MOV",
    "mts",
    "MTS",
```
- ファイル名形式は何でもOK（Exifの撮影日時で判定）
- Exifの撮影日時が無いファイルは整理されない
- 撮影日時が同じファイルは別名で保存
- サブディレクトリは対象外(再帰的には実行されない)

```txt
 -------------------
 実行前
 -------------------
 tests/data-org
 ├── IMG_2031.jpg
 ├── IMG_2031a.jpg
 ├── IMG_2031b.jpg
 ├── IMG_2031b.HEIC  ※対象外の拡張子なので移動されない
 ├── exifcleaner-for-mac-Hero.jpeg  ※Exifが無いので移動されない
 └── sub
      └── IMG_2031.mov  ※サブディレクトリは移動されない

 ↓

 -------------------
 実行後
 -------------------
 tests/data-tmp
 └── 20220821
      ├── 2022-08-21_10-13-58.jpg
      ├── 2022-08-21_10-13-58-01.jpg  ※撮影日時が同じファイルは別名で保存
      └── 2022-08-21_10-13-58-02.jpg  ※撮影日時が同じファイルは別名で保存
```

## Usage

Environmental variables

- 結果をLINE, slack通知する場合に必要 (通知しなければ不要)
- 下記`.env`ファイルをproject rootに配置 (エンコードはUTF-8)

```txt
slack_post_url="<slack_post_url>"
slack_post_channel="<slack_post_channel>"
line_post_url="<line_post_url>"
```

Requirement

ffmpegが必要(動画の撮影日時取得に使用)

```sh
# Mac
brew install ffmpeg
```

Windowsは[https://ffmpeg.org/](https://ffmpeg.org/)からダウンロード

Install

```sh
pip install git+https://github.com/mozkzki/tidydir
# upgrade
pip install --upgrade git+https://github.com/mozkzki/tidydir
# uninstall
pip uninstall tidydir
```

実行

`./tests/data-org`ディレクトリ以下のファイルが`./tests/data-tmp`ディレクトリ以下の日付フォルダに整理される。

```sh
tidydir ./tests/data-org ./tests/data-tmp
```

## Develop

base project: [mozkzki/moz-sample](https://github.com/mozkzki/moz-sample)

### Prepare

```sh
poetry install
poetry shell
```

### Run (Example)

```sh
tidydir ./tests/data-org ./tests/data-tmp
# or
make start
```

### Unit Test

test all.

```sh
pytest
pytest -v # verbose
pytest -s # show standard output (same --capture=no)
pytest -ra # show summary (exclude passed test)
pytest -rA # show summary (include passed test)
```

with filter.

```sh
pytest -k app
pytest -k test_app.py
pytest -k my
```

specified marker.

```sh
pytest -m 'slow'
pytest -m 'not slow'
```

make coverage report.

```sh
pytest -v --capture=no --cov-config .coveragerc --cov=src --cov-report=xml --cov-report=term-missing .
# or
make ut
```

### Lint

```sh
flake8 --max-line-length=100 --ignore=E203,W503 ./src
# or
make lint
```

### Update dependency modules

dependabot (GitHub公式) がプルリクを挙げてくるので確認してマージする。

- 最低でもCircleCIが通っているかは確認
- CircleCIでは、最新の依存モジュールでtestするため`poetry update`してからtestしている
- dependabotは`pyproject.toml`と`poetry.lock`を更新してくれる
