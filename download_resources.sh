#! /bin/bash

mkdir -p osadl
mkdir -p spdx

pushd osadl

./download.sh

popd

python3 spdx_download.py

./spdx/download_fulltext.sh
