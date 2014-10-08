from PyQt4.QtCore import *
from PyQt4.QtGui import *
from time import sleep
import random

class Producer(QThread):

  def __init__(self,parent,data):
    QThread.__init__(self,parent)
    self.data = data
    self.min_x=0
    self.max_x=0
    self.pause = False

  def init(self):
    pass

  def openPreference(self,parent):
    pref = QDialog(parent)
    layout = QGridLayout()

    y_offset_label = QLabel("Y Offset")
    y_offset = QSpinBox(parent)
    y_offset.setMinimum(-1000)
    y_offset.setMaximum(1000)
    y_offset.setSingleStep(10)

    speed_label = QLabel("Delay ms")
    speed = QDoubleSpinBox(parent)
    speed.setSingleStep(0.1)
    speed.setMinimum(0.0)
    speed.setMaximum(10)
    speed.setValue(0.01)

    from_label = QLabel("From")
    from_rnd = QSpinBox(parent)

    to_label = QLabel("To")
    to_rnd = QSpinBox(parent)
    to_rnd.setValue(50)

    buttons = QDialogButtonBox(
                            QDialogButtonBox.Ok,
                            Qt.Horizontal, pref)

    buttons.accepted.connect(pref.accept)

    layout.addWidget(y_offset_label,0,0)
    layout.addWidget(y_offset,0,1)
    layout.addWidget(speed_label,1,0)
    layout.addWidget(speed,1,1)
    layout.addWidget(from_label,2,0)
    layout.addWidget(from_rnd,2,1)
    layout.addWidget(to_label,3,0)
    layout.addWidget(to_rnd,3,1)
    layout.addWidget(buttons,4,0,1,2)
    pref.setLayout(layout)
    pref.exec_()

    # save preference
    self.y_offset = y_offset.value()
    self.from_rnd = from_rnd.value()
    self.to_rnd = to_rnd.value()
    self.speed = speed.value()


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
      rnd = random.randint(self.from_rnd,self.to_rnd) + self.y_offset
      dt = datetime.now() - start_time
      if items>100:
        del self.data[0][0]
        del self.data[1][0]
        self.min_x = self.data[0][0]

      ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
      self.max_x = ms if ms>self.max_x else self.max_x

      self.data[0].append(ms)
      self.data[1].append(rnd)
      sleep(self.speed)


