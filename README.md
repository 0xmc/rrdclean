# rrdclean

Forked from https://github.com/mhagander/rrdclean

Features of this version
* Python3
* Temp files instead of mucking about with stdin and pipes
* Interactive to remove all spikes, not prompted for each individual one
* Friendly thresholds (1.2k instead of 1200)
* Remove all values in row above threshold, not just the first one

## Using
Install
```shell
python3 setup.py build
python3 setup.py install  # may need sudo
```
Run
```shell
python3 -m rrdclean FILE THRESHOLD
```

## Developing
Install
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements-dev.txt
```
Before PR
```shell
tox
```
