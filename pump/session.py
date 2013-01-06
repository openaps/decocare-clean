import logging
import time

log = logging.getLogger( ).getChild(__name__)
import commands
import lib
import stick
from errors import StickError, AckError, BadDeviceCommError


class Session(object):
  def __init__(self, stick):
    self.stick = stick
    self.should_download = True
  def init(self, skip_power_control=False):
    stick = self.stick
    log.info('test fetching product info %s' % stick)
    log.info(pformat(stick.product_info( )))
    log.info('get signal strength of %s' % stick)
    signal = 0
    while signal < 50:
      signal = stick.signal_strength( )
    log.info('we seem to have found a nice signal strength of: %s' % signal)
  def end(self):
    stick = self.stick
    log.info(pformat(stick.usb_stats( )))
    log.info(pformat(stick.radio_stats( )))

  def execute(self, command):
    self.command = command
    for i in xrange(max(1, self.command.retries)):
      log.info('execute attempt: %s' % (i + 1))
      try:
        self.expectedLength = self.command.bytesPerRecord * self.command.maxRecords
        self.transfer( )
        if self.should_download:
          log.info('sleeping %s before download' % command.effectTime)
          time.sleep(command.effectTime)
          self.download( )
        return
      except BadDeviceCommError, e:
        log.critical("ERROR: %s" % e)
        # self.clearBuffers( )
    log.critical('this seems like a problem')

  def download(self):
    errors = [ ]
    if self.expectedLength > 0:
      for i in xrange(3):
        try:
          log.info('proceeding with download')
          data = self.stick.download( )
          self.command.data = data
          return data
        except AckError, e:
          time.sleep(.010)
          log.error(e)
          errors.append(e)
    else:
      log.info('no download required')
    assert not errors, ("with errors:%s" %"\n".join( map(str, errors) ))
  def transfer(self):
    log.info('session transferring packet')
    self.stick.transmit_packet(self.command)

class Pump(Session):
  def __init__(self, stick, serial='208850'):
    super(type(self), self).__init__(stick)
    self.serial = serial
    log.info('setting up to talk with %s' % serial)

  def power_control(self):
    return self.query(commands.PowerControl)
    self.should_download = True
    try:
      self.download( )
      size = self.stick.poll_size( )
      log.info("SIZE %s" % size)
    except BadDeviceCommError, e:

      # self.stick.download_packet(size)
      download = stick.ReadRadio(size)
      log.info("power_control download_packet:%s" % (size))

      self.stick.command = download
      packet = None
      try:
        packet = self.stick.process( )
      except BadDeviceCommError, e:
        raw = self.stick.link.read(64)
        ack, body = download.respond(raw)
        packet = download.parse(body)
      return packet
      
    #try:
    #  log.info('try to poll without download' % self.stick.poll_size( ))
    #except AckError, e:
    #  log.info('try again to poll without download' % self.stick.poll_size( ))

  def read_model(self):
    model = self.query(commands.ReadPumpModel)
    self.model = model
    return model

  def query(self, Command):
    command = Command(serial=self.serial)
    self.execute(command)
    return command

if __name__ == '__main__':
  import doctest
  doctest.testmod( )

  import sys
  port = None
  port = sys.argv[1:] and sys.argv[1] or False
  serial_num = sys.argv[2:] and sys.argv[2] or False
  if not port or not serial_num:
    print "usage:\n%s <port> <serial>, eg /dev/ttyUSB0 208850" % sys.argv[0]
    sys.exit(1)
  import link
  import stick
  from pprint import pformat
  logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
  log.info("howdy! I'm going to take a look at your pump.")
  stick = stick.Stick(link.Link(port, timeout=.100))
  stick.open( )
  session = Pump(stick, '208850')
  log.info(pformat(stick.interface_stats( )))
  #log.info("POWER CONTROL ON")
  #session.power_control( )
  #log.info(pformat(stick.interface_stats( )))
  log.info('PUMP MODEL: %s' % session.read_model( ))
  log.info(pformat(stick.interface_stats( )))
  # stick.open( )
  
#####
# EOF