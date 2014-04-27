

dt=$(date +%Y%m%d_%H%M%S)
sudo ./bin/mm-send-comm.py --init --prefix-path logs/$dt- --serial 584923 --port /dev/ttyUSB0 tweak ReadGlucoseHistory --page 17 --save | tee analysis/pg-17-$dt-ReadGlucoseHistory.markdown
sudo ./bin/mm-send-comm.py --prefix-path logs/$dt- --serial 584923 --port /dev/ttyUSB0 tweak ReadISIGHistory --page 17 --save | tee analysis/pg-17-$dt-ReadISIGHistory.markdown

