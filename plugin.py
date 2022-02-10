import time
import threading
import serial


class Plugin:
  CONFIG=[
    {
      'name': 'device',
      'description': 'set to the device path (alternative to usbid)',
      'default': ''
    },
    {
      'name': 'usbid',
      'description': 'set to the usbid of the device (alternative to device)',
      'default': ''
    }
  ]
  @classmethod
  def pluginInfo(cls):
    """
    the description for the module
    @return: a dict with the content described below
            parts:
               * description (mandatory)
               * data: list of keys to be stored (optional)
                 * path - the key - see AVNApi.addData, all pathes starting with "gps." will be sent to the GUI
                 * description
    """
    return {
      'description': 'seatalk 1 protocol generator',
      'config': cls.CONFIG,
      'data': [
      ]
    }

  def __init__(self,api):
    """
        initialize a plugins
        do any checks here and throw an exception on error
        do not yet start any threads!
        @param api: the api to communicate with avnav
        @type  api: AVNApi
    """
    self.api = api # type: AVNApi
    #we register an handler for API requests
    self.lastReceived=0
    self.isConnected=False
    self.connection=None
    self.device=None
    self.isBusy=False
    self.condition=threading.Condition()
    if hasattr(self.api,'registerEditableParameters'):
      self.api.registerEditableParameters(self.CONFIG,self._changeConfig)
    if hasattr(self.api,'registerRestart'):
      self.api.registerRestart(self._apiRestart)
    self.changeSequence=0
    self.startSequence=0

  def _apiRestart(self):
    self.startSequence+=1
    self.changeSequence+=1

  def _changeConfig(self,newValues):
    self.api.saveConfigValues(newValues)
    self.changeSequence+=1

  def getConfigValue(self,name):
    defaults=self.pluginInfo()['config']
    for cf in defaults:
      if cf['name'] == name:
        return self.api.getConfigValue(name,cf.get('default'))
    return self.api.getConfigValue(name)

  def run(self):
    startSequence=self.startSequence
    while startSequence == self.startSequence:
      try:
        #only AvNav after 20210224
        self.api.deregisterUsbHandler()
      except:
        pass
      self.runInternal()

  def runInternal(self):
    """
    the run method
    this will be called after successfully instantiating an instance
    this method will be called in a separate Thread
    The plugin sends every 10 seconds the depth value via seatalk
    @return:
    """
    changeSequence=self.changeSequence
    seq=0
    self.api.log("started")
    enabled=self.getConfigValue('enabled')
    if enabled is not None and enabled.lower()!='true':
      self.api.setStatus("INACTIVE", "disabled by config")
      return
    usbid=None
    try:
      self.device=self.getConfigValue('device')
      usbid=self.getConfigValue('usbid')
      if usbid == '':
        usbid=None
      if self.device == '':
        self.device=None
      if self.device is None and usbid is None:
        raise Exception("missing config value device or usbid")

      if self.device is not None and usbid is not None:
        raise Exception("only one of device or usbid can be set")
    except Exception as e:
      self.api.setStatus("ERROR", "config error %s "%str(e))
      while changeSequence == self.changeSequence:
        time.sleep(0.5)
      return
    if usbid is not None:
      self.api.registerUsbHandler(usbid,self.deviceConnected)
      self.api.setStatus("STARTED", "using usbid %s, baud=4800" % (usbid))
    else:
      self.api.setStatus("STARTED","using device %s, baud=4800"%(self.device))
    connectionHandler=threading.Thread(target=self.handleConnection, name='seatalk-remote-connection')
    connectionHandler.setDaemon(True)
    connectionHandler.start()
    while changeSequence == self.changeSequence:
      if not self.isConnected:
        return {'status': 'not connected'}
      try:
        # send command byte 0x00 with parity bit set
        send = bytearray([0x00,0x02])
        self.connection.write(send)
        self.connection.flushOutput()
        self.connection.flush()
        time.sleep(3)

        # send  Attribute 0x02, Adddata 0x12&0x34 with parity bit reset
        self.connection.parity = serial.PARITY_SPACE
        self.connection.close()
        self.connection.open()
        send = bytearray([0x00,0x11,0x22])
        self.connection.write(send)
        self.connection.flushOutput()
        self.connection.flush()

        self.connection.parity = serial.PARITY_MARK
        self.connection.close()
        self.connection.open()
        time.sleep(3)

        self.api.log("SEATALK frame written")
        
      except Exception as e:
        self.api.error("unable to send command to %s: %s" % (self.device, str(e)))

      time.sleep(1)

  def handleConnection(self):
    changeSequence=self.changeSequence
    errorReported=False
    lastDevice=None
    while changeSequence == self.changeSequence:
      if self.device is not None:
        if self.device != lastDevice:
          self.api.setStatus("STARTED", "trying to connect to %s at 4800" % (self.device))
          lastDevice=self.device
        #on windows we would need an integer as device...
        try:
          pnum = int(self.device)
        except:
          pnum = self.device
        self.isConnected=False
        self.isBusy=False
        try:
          self.connection = serial.Serial(port=pnum, baudrate=4800, bytesize=serial.EIGHTBITS, parity=serial.PARITY_MARK, stopbits=serial.STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, dsrdtr=False)
          self.api.setStatus("SEATALK1","connected to %s at 4800"%(self.device))
          self.api.log("connected to %s at 4800" % (self.device))
          self.isConnected=True
          errorReported=False
          #continously read data to get an exception if disconnected
          while True:
            self.connection.readline(10)
        except Exception as e:
          if not errorReported:
            self.api.setStatus("ERROR","unable to connect/connection lost to %s: %s"%(self.device, str(e)))
            self.api.error("unable to connect/connection lost to %s: %s" % (self.device, str(e)))
            errorReported=True
          self.isConnected=False
          time.sleep(1)
      time.sleep(1)

  def deviceConnected(self,device):
    if self.device == device:
      return
    try:
      if self.connection is not None:
        self.connection.close()
    except:
      pass
    self.connection=None
    self.api.log("device connected %s",device)
    self.device=device

  def sendCommand(self,val):
    #we avoid blocking multiple threads here
    canWrite=False
    self.condition.acquire()
    if not self.isBusy:
      self.isBusy=True
      canWrite=True
    self.condition.release()
    if not canWrite:
      raise Exception("busy")
    try:
      self.connection.write((val).encode('ascii'))
    except Exception as e:
      self.condition.acquire()
      self.isBusy=False
      self.condition.release()
      raise
    self.condition.acquire()
    self.isBusy = False
    self.condition.release()

