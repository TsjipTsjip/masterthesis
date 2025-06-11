#! /bin/bash

rm *.json

wget -4 https://www.osadl.org/fileadmin/checklists/matrixseqexpl.json
wget -4 https://www.osadl.org/fileadmin/checklists/copyleft.json

# Download unreflicenses
mkdir -p unreflicenses
pushd unreflicenses

./download.sh

popd

# Download actions
mkdir -p actions
pushd actions

./download.sh

popd

# Download language
mkdir -p language
pushd language

./download.sh

popd

# Download terms
mkdir -p terms
pushd terms

./download.sh

popd