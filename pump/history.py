#!/usr/bin/python
"""
This module provides some basic helper/formatting utilities,
specifically targeted at decoding ReadHistoryData data.

"""
import sys
from binascii import hexlify
from datetime import datetime

import lib

class NotADate(Exception): pass

class Mask:
  time   = 0xC0
  invert = 0x3F
  year   = 0x0F


def quick_hex(bb):
  return ' '.join( [ '%#04x' % x for x in bb ] )

def parse_seconds(sec):
  """
  >>> parse_seconds(0x92)
  18
  """
  return sec & Mask.invert

def parse_minutes(minutes):
  """
  >>> parse_minutes(0x9e)
  30
  """
  return minutes & Mask.invert


def parse_hours(hours):
  """
  >>> parse_hours(0x0b)
  11

  >>> parse_hours(0x28)
  8

  """
  return int(hours & 0x1f)

def parse_day(day):
  """
  >>> parse_day( 0x01 )
  1
  """
  return day & Mask.year

def parse_months(seconds, minutes):
  """
  >>> parse_months( 0x92, 0x9e )
  10

  """
  high = (seconds & Mask.time) >> 4
  low  = (minutes & Mask.time) >> 6
  return high | low

def parse_years_lax(year):
  y = (year & Mask.year) + 2000
  return y


_remote_ids = [
  bytearray([ 0x01, 0xe2, 0x40 ]),
  bytearray([ 0x03, 0x42, 0x2a ]),
  bytearray([ 0x0c, 0x89, 0x92 ]),
]

def decode_remote_id(msg):
  """
   0x27
   0x01 0xe2 0x40
   0x03 0x42 0x2a
   0x28 0x0c 0x89
   0x92 0x00 0x00 0x00

  >>> decode_remote_id(_remote_ids[0])
  '123456'

  >>> decode_remote_id(_remote_ids[1])
  '213546'

  >>> decode_remote_id(_remote_ids[2])
  '821650'



  """
  high   = msg[ 0 ] * 256 * 256
  middle = msg[ 1 ] * 256
  low    = msg[ 2 ]
  return str(high + middle + low)


def extra_year_bits(year=0x86):
  """
  >>> extra_year_bits( )
  [1, 0, 0, 0]

  >>> extra_year_bits(0x06)
  [0, 0, 0, 0]

  >>> extra_year_bits(0x86)
  [1, 0, 0, 0]

  >>> extra_year_bits(0x46)
  [0, 1, 0, 0]

  >>> extra_year_bits(0x26)
  [0, 0, 1, 0]

  >>> extra_year_bits(0x16)
  [0, 0, 0, 1]

  """
  # year = year[0]
  masks = [ ( 0x80, 7), (0x40, 6), (0x20, 5), (0x10, 4) ]
  nibbles = [ ]
  for mask, shift in masks:
    nibbles.append( ( (year & mask) >> shift ) )
  return nibbles
  
def extra_hour_bits(value):
  """
  >>> extra_hour_bits(0x28)
  [0, 0, 1]

  >>> extra_hour_bits(0x8)
  [0, 0, 0]
  """
  masks = [ ( 0x80, 7), (0x40, 6), (0x20, 5), ]
  nibbles = [ ]
  for mask, shift in masks:
    nibbles.append( ( (value & mask) >> shift ) )
  return nibbles
  

def parse_years(year):
  """
    >>> parse_years(0x06)
    2006

  """
  # if year > 0x80:
  #  year = year - 0x80
  y = (year & Mask.year) + 2000
  # if y < 0 or y < 1999 or y > 2015:
  #   raise ValueError(y)
  return y

def encode_year(year):
  pass

def encode_monthbyte(sec=18, minute=30, month=10):
  """
  >>> encode_monthbyte( ) == bytearray(b'\x92\x9e')
  True

  >>> quick_hex(encode_monthbyte( ))
  '0x92 0x9e'

  >>> encode_monthbyte(sec=10) == bytearray(b'\x8a\x9e')
  True

  >>> encode_monthbyte(sec=35) == bytearray(b'\xa3\x9e')
  True

  >>> encode_monthbyte(sec=50) == bytearray(b'\xb2\x9e')
  True

  >>> encode_monthbyte(minute=10) == bytearray(b'\x92\x8a')
  True

  >>> encode_monthbyte(minute=35) == bytearray(b'\x92\xa3')
  True

  >>> encode_monthbyte(minute=50) == bytearray(b'\x92\xb2')
  True

  >>> encode_monthbyte(month=1) == bytearray(b'\x12^')
  True

  >>> encode_monthbyte(month=2) == bytearray(b'\x12\x9e')
  True

  >>> encode_monthbyte(month=3) ==  bytearray(b'\x12\xde')
  True

  >>> encode_monthbyte(month=10, minute=0, sec=0) == bytearray(b'\x80\x80')
  True

  >>> encode_monthbyte(month=10, minute=0, sec=24) == bytearray(b'\x98\x80')
  True

  """

  encoded = [ 0x00, 0x00 ]


  high = (month & (0x3 << 2)) >> 2
  low  = month & (0x3)

  encoded[0] = sec | (high << 6)
  encoded[1] = minute | (low << 6)
  return bytearray( encoded )

  printf("0x%.2x 0x%.2x\n", buf[0], buf[1]);

def encode_minute(minute=30, month=10):
  """
  >>> quick_hex(encode_minute( ))
  '0x9e'

  """
  low  = month & (0x3)
  encoded = minute | (low << 6)
  return bytearray( [ encoded ] )

def encode_second(sec=18, month=10):
  """
  >>> encode_second( ) == bytearray(b'\x92')
  True

  >>> quick_hex(encode_second( ))
  '0x92'

  """
  high = (month & (0x3 << 2)) >> 2
  encoded = sec | (high << 6)
  return bytearray( [ encoded ] )

def test_time_encoders( ):
  """
  >>> test_time_encoders( )
  True
  """

  one = bytearray().join([encode_second( ), encode_minute( )])
  two = encode_monthbyte( )
  return one == two

def unmask_date(data):
  """
  Extract date values from a series of bytes.

  Returns 6-tuple of scalar values year, month, day, hours, minutes,
  seconds.
  >>> unmask_date(bytearray( [ 0x6f, 0xd7, 0x08, 0x01, 0x06 ] ))
  (2006, 7, 1, 8, 23, 47)

  >>> unmask_date( bytearray( [ 0x00 ] * 5 ))
  (2000, 0, 0, 0, 0, 0)


  These examples are invalid dates/not found in CSV, here just for
  testing purposes.
  >>> unmask_date( bytearray( [ 0x93, 0xd4, 0x0e, 0x10, 0x0c ] ))
  (2012, 11, 0, 14, 20, 19)

  >>> unmask_date( bytearray( [ 0xa6, 0xeb, 0x0b, 0x10, 0x0c, ] ))
  (2012, 11, 0, 11, 43, 38)

  >>> unmask_date( bytearray( [ 0x95, 0xe8, 0x0e, 0x10, 0x0c ] ))
  (2012, 11, 0, 14, 40, 21)

  >>> unmask_date( bytearray( [ 0x80, 0xcf, 0x30, 0x10, 0x0c, ] ))
  (2012, 11, 0, 16, 15, 0)

  >>> unmask_date( bytearray( [ 0xa3, 0xcf, 0x30, 0x10, 0x0c, ] ))
  (2012, 11, 0, 16, 15, 35)


  """
  data = data[:]
  seconds = parse_seconds(data[0])
  minutes = parse_minutes(data[1])

  hours   = parse_hours(data[2])
  day     = parse_day(data[3])
  year    = parse_years(data[4])

  month   = parse_months( data[0], data[1] )
  return (year, month, day, hours, minutes, seconds)

_bewest_dates = {
  # from https://github.com/bewest/decoding-carelink/blob/rewriting/analysis/bewest-pump/ReadHistoryData-page-19.data.list_opcodes.markdown
  'page-19': {
    0:  [ 0xaa, 0xf7, 0x40, 0x0c, 0x0c, ],
    1:  [ 0x40, 0x0c, 0x0c, 0x0a, 0x0c, ],
    2:  [ 0x0c, 0x8b, 0xc3, 0x28, 0x0c, ],
    3:  [ 0x8b, 0xc3, 0x28, 0x0c, 0x8c, ],
    4:  [ 0x28, 0x0c, 0x8c, 0x5b, 0x0c, ],
    5:  [ 0x8d, 0xc3, 0x08, 0x0c, 0x0c, ],
    6:  [ 0xaa, 0xf7, 0x00, 0x0c, 0x0c, ],
  }
}

def _test_decode_bolus( ):
  """
  ## correct
  >>> parse_date( bytearray( _bewest_dates['page-19'][6] ) ).isoformat( )
  '2012-11-12T00:55:42'

  ## correct
  >>> parse_date( bytearray( _bewest_dates['page-19'][0] ) ).isoformat( )
  '2012-11-12T00:55:42'

  ## this is wrong
  >>> parse_date( bytearray( _bewest_dates['page-19'][1] ) ).isoformat( )
  '2012-04-10T12:12:00'

  ## day,month is wrong, time H:M:S is correct
  # expected: 
  >>> parse_date( bytearray( _bewest_dates['page-19'][2] ) ).isoformat( )
  '2012-02-08T03:11:12'

  ## correct
  >>> parse_date( bytearray( _bewest_dates['page-19'][3] ) ).isoformat( )
  '2012-11-12T08:03:11'


  #### not a valid date
  # >>> parse_date( bytearray( _bewest_dates['page-19'][4] ) ).isoformat( )

  ## correct
  >>> parse_date( bytearray( _bewest_dates['page-19'][5] ) ).isoformat( )
  '2012-11-12T08:03:13'


  """
  """

  0x5b 0x7e # bolus wizard,
  0xaa 0xf7 0x00 0x0c 0x0c # page-19[0]

  0x0f 0x50 0x0d 0x2d 0x6a 0x00 0x0b 0x00
  0x00 0x07 0x00 0x0b 0x7d 0x5c 0x08 0x58
  0x97 0x04 0x30 0x05 0x14 0x34 0xc8
  0x91 0xf8      # 0x91, 0xf8 = month=11, minute=56, seconds=17!
  0x00           # general parsing fails here
  0x00
  0xaa 0xf7 0x40 0x0c 0x0c # expected  - page-19[6]

  0x0a 0x0c 
  0x8b 0xc3 0x28 0x0c 0x8c # page-19[3]


  0x5b 0x0c

  0x8d 0xc3 0x08 0x0c 0x0c # page-19[5]
  0x00 0x51 0x0d 0x2d 0x6a 0x1f 0x00 0x00 0x00 0x00 0x00
  """

### csv deconstructed
"""
395,11/12/12,00:55:42,11/12/12 00:55:42,Normal 1.1,1.1,BolusNormal
  "AMOUNT=1.1, CONCENTRATION=null, PROGRAMMED_AMOUNT=1.1,
  ACTION_REQUESTOR=pump, ENABLE=true, IS_DUAL_COMPONENT=false,
  UNABSORBED_INSULIN_TOTAL=null",9942920032,51974238,2086,Paradigm 522

396,11/12/12,00:56:17,11/12/12 00:56:17 JournalEntryPumpLowReservoir
  "AMOUNT=20, ACTION_REQUESTOR=pump",9942920033,51974238,2087,Paradigm 522


397,11/12/12,08:03:11,11/12/12 08:03:11 268 CalBGForPH
  "AMOUNT=268, ACTION_REQUESTOR=pump",9942920031,51974238,2085,Paradigm 522

398,11/12/12,08:03:13,11/12/12 08:03:13 UnabsorbedInsulin
  "BOLUS_ESTIMATE_DATUM=9942920029, INDEX=0, AMOUNT=1.1, RECORD_AGE=429,
  INSULIN_TYPE=null,
  INSULIN_ACTION_CURVE=240",9942920030,51974238,2084,Paradigm 522

399,11/12/12,08:03:13,11/12/12 08:03:13
  3.1,125,106,13,45,0,268,3.1,0,0.0
  BolusWizardBolusEstimate,"BG_INPUT=268, BG_UNITS=mg dl,
  CARB_INPUT=0, CARB_UNITS=grams, CARB_RATIO=13,
  INSULIN_SENSITIVITY=45, BG_TARGET_LOW=106, BG_TARGET_HIGH=125,
  BOLUS_ESTIMATE=3.1, CORRECTION_ESTIMATE=3.1, FOOD_ESTIMATE=0,
  UNABSORBED_INSULIN_TOTAL=0, UNABSORBED_INSULIN_COUNT=1,
  ACTION_REQUESTOR=pump",9942920029,51974238,2083,Paradigm 522

400,11/12/12,08:03:13,11/12/12 08:03:13 Normal
  3.1,3.1 BolusNormal "AMOUNT=3.1, CONCENTRATION=null,
  PROGRAMMED_AMOUNT=3.1, ACTION_REQUESTOR=pump, ENABLE=true,
  IS_DUAL_COMPONENT=false,
  UNABSORBED_INSULIN_TOTAL=null",9942920028,51974238,2082,Paradigm 522

401,11/12/12,08:50:31,11/12/12 08:50:31 JournalEntryPumpLowReservoir
  "AMOUNT=10, ACTION_REQUESTOR=pump",9942920027,51974238,2081,Paradigm 522

"""
def parse_date(data):
  """
  Apply strict datetime validation to extract a datetime from a series
  of bytes.
  >>> parse_date(bytearray( [ 0x6f, 0xd7, 0x08, 0x01, 0x06 ] )).isoformat( )
  '2006-07-01T08:23:47'


  """
  (year, month, day, hours, minutes, seconds) = unmask_date(data)
  try:
    date = datetime(year, month, day, hours, minutes, seconds)
    return date
  except ValueError, e:
    raise NotADate(e)


_bad_days = [
    bytearray([ 0xa9, 0xf5, 0x15, 0x14, 0x0c, ]),
    bytearray([ 0xa6, 0xc7, 0x36, 0x14, 0x8c, ]),
    bytearray([ 0xa9, 0xf5, 0x15, 0x14, 0x0c, ]),
    bytearray([ 0xa6, 0xc7, 0x36, 0x14, 0x8c, ]),

    bytearray([ 0xa2, 0xe9, 0x10, 0x19, 0x0c, ]),
    bytearray([ 0xa0, 0xf6, 0x0d, 0x19, 0x0c, ]),
    bytearray([ 0xa5, 0xd9, 0x34, 0x1d, 0x0c, ]),

    bytearray([ 0xc2, 0x3b, 0x0e, 0x14, 0x0c, ]),
    bytearray([ 0xd9, 0x1c, 0x0f, 0x14, 0x0c, ]),
  ]

# don't think we have days incorrect. observe:
def bad_days(x=0):
  """
    # page 17, RECORD 11
    >>> parse_date( bad_days(0) ).isoformat( )
    '2012-11-20T21:53:41'

    # page 17, ~ RECORD 12
    >>> parse_date( bad_days(1) ).isoformat( )
    '2012-11-20T22:07:38'

    >>> parse_date( bad_days(2) ).isoformat( )
    '2012-11-20T21:53:41'

    >>> parse_date( bad_days(3) ).isoformat( )
    '2012-11-20T22:07:38'

    # page 16, RECORD ~15
    >>> parse_date( bad_days(4) ).isoformat( )
    '2012-11-25T16:41:34'

    >>> parse_date( bad_days(5) ).isoformat( )
    '2012-11-25T13:54:32'

    # page 15
    >>> parse_date( bad_days(6) ).isoformat( )
    '2012-11-29T20:25:37'

    # page 0
    >>> parse_date( bad_days(7) ).isoformat( )
    '2012-12-20T14:59:02'

    >>> parse_date( bad_days(8) ).isoformat( )
    '2012-12-20T15:28:25'

  """
  return _bad_days[x]



if __name__ == '__main__':
  import doctest
  doctest.testmod( )

#####
# EOF
