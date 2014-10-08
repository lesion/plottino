from PyQt4.QtCore import *
from PyQt4.QtGui import *
import glob

class Producer(QThread):

  def __init__(self,parent,data):
    QThread.__init__(self,parent)
    self.data = data
    self.min_x=0
    self.max_x=0
    self.pause = False

  def enumerate_serial_ports(self):
      """
      Purpose:        scan for available serial ports
      Return:         return a list of of the availables ports names
      """
      return glob.glob('/dev/tty*')

  def openPreference(self,parent):
    pref = QDialog(parent)
    layout = QGridLayout()

    port_label = QLabel("Port")
    port = QComboBox(parent)
    port.addItems(self.enumerate_serial_ports())

    baud_label = QLabel("Baud Rate")
    baud = QComboBox(parent)
    available_baudrates = ['4800','9600','19200']
    baud.addItems(available_baudrates)

    buttons = QDialogButtonBox(
                            QDialogButtonBox.Ok,
                            Qt.Horizontal, pref)

    buttons.accepted.connect(pref.accept)

    layout.addWidget(port_label,0,0)
    layout.addWidget(port,0,1)
    layout.addWidget(baud_label,1,0)
    layout.addWidget(baud,1,1)
    layout.addWidget(buttons,2,0,1,2)
    pref.setLayout(layout)
    pref.exec_()

    # save preference
    self.port = str(port.currentText())
    self.baud = int(baud.currentText())

  def init(self):
      from serial import Serial
      try:
        self.serial = Serial(self.port,self.baud)
        return True
      except Exception as e:
        print e.value
        return e.value


  def run(self):
    from datetime import datetime

    start_time = datetime.now()
    items = 0
    self.min_x=0
    self.max_x=0

    while True:
      while(self.pause):
        QThread.msleep(100)

      items+=1
      data = int(self.serial.readline())
      dt = datetime.now() - start_time
      if items>100:
        del self.data[0][0]
        del self.data[1][0]
        self.min_x = self.data[0][0]

      ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
      self.max_x = ms if ms>self.max_x else self.max_x
      self.data[0].append(ms)
      self.data[1].append(data)
