rrdclean
========

Forked from https://github.com/mhagander/rrdclean

Modified
* python2 -> python3
* temp files instead of mucking about with stdin and pipes
* interactive to remove all spikes, not prompted for each individual one
* friendly thresholds (1.2k instead of 12000)
* remove all values in row above threshold, not just the first one
