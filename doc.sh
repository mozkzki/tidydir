#!/bin/sh

if [ -e docs/conf.py ]; then
    sphinx-apidoc -f -o docs/ myapp/  # 2回目以降
else
    sphinx-apidoc -F -o docs/ myapp/  # 初回実行
fi
make -C docs/ html
