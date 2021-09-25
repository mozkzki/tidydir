# tidydir

指定ディレクトリ内のファイルを日付フォルダに整理する。
スマホやカメラの画像/動画ファイルの日付整理を想定。

- 日付は下記の形式であること
- サブディレクトリは対象外(再帰的には実行されない)

```txt
 -------------------
 実行前
 -------------------
 tests/data
 ├── 2020-01-01 10.10.10.jpg
 ├── 2020-05-05 12.12.12.mov

 ↓

 -------------------
 実行後
 -------------------
 tests/data
 ├── 20200101
 │   └── 2020-01-01 10.10.10.jpg
 ├── 20200505
 │   └── 2020-05-05 12.12.12.mov
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

Install

```sh
pip install git+https://github.com/mozkzki/tidydir
# upgrade
pip install --upgrade git+https://github.com/mozkzki/tidydir
# uninstall
pip uninstall tidydir
```

実行

`./tests/data`ディレクトリ以下のファイルが日付フォルダに整理される。

```sh
tidydir ./tests/data
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
tidydir ./tests/data
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
