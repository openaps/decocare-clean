#/bin/bash
# make an example of an interesting log worth sharing

( cat $0
  date
  time python pump/stick.py /dev/ttyUSB0
  time python pump/session.py /dev/ttyUSB0 208850
) | tee status-quo.log

#####
# EOF
