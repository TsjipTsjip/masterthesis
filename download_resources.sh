#! /bin/bash

mkdir -p osadl
mkdir -p spdx

pushd osadl

./download.sh

popd

python3 spdx_download.py

pushd spdx

./download.sh

popd