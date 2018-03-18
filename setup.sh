# Author: Hansheng Zhao <copyrighthero@gmail.com> (https://www.zhs.me)
#! /bin/bash

# Variable definitions
DIRECTORY=''

# Create Python virtual environment
python3 -m venv --symlinks ./

# Activate Python virtual environment
source bin/activate

# Install pre-requisites
bin/pip3 install --upgrade -r ./requirements.txt

# Install external library
# sed -e '1,/^__BOUNDARY__$/d' $0 | base64 -d | tar xzv
# pushd ${DIRECTORY}
# python3 setup.py install
# popd
# rm -rf ${DIRECTORY}

# Finalize setup procedures
deactivate

# Avoid executing encoded payload
exit 0

# External Base64 encoded tar.gz library
__BOUNDARY__
