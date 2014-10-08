from PyQt4.QtCore import *
from PyQt4.QtGui import *
from time import sleep

class Producer(QThread):

  def __init__(self,parent,data):
    QThread.__init__(self,parent)
    self.data = data
    self.min_x=0
    self.max_x=0
    self.pause = False
    self.path = None
    self.separator = None

  def init(self):
    self.fd=open(self.path)

    """  supported format
    123
    1.2
    1,2
    1|2
    1.2|2.3

    """

    line = self.fd.readline()
    line = line.strip()
    print "Line found"
    print line

    # found how the data is formatted
    if line.isdigit():
        self.fd.seek(0)
        print "Dai dai dai sono un numero "
        return True
    try:
        float(line)
        self.fd.seek(0)
        return True
    except ValueError:
        pass

    separator = None
    for char in line:
        if not char.isdigit() and char!='.':
            if separator!=None:
                return False
            separator=char

    self.fd.seek(0)
    self.separator = separator
    return True



  def openPreference(self,parent):
    from os import path
    self.path = QFileDialog.getOpenFileName(None,"Open File","~")
    if not path.isfile(self.path):
      return False
    else:
      return True


  def run(self):
    items = 0
    self.min_x=0
    self.max_x=0

    while True:
      line = self.fd.readline()
      if line=='':
          self.fd.close()
          self.terminate()

      line = line.strip()
      items+=1

      if self.separator:
        data = line.split(self.separator)
        x = float(data[0])
        y = float(data[1])
      else:
        x=items
        y=float(line)

      self.max_x = x if x>self.max_x else self.max_x
      self.min_x = x if x<self.min_x else self.min_x

      self.data[0].append(x)
      self.data[1].append(y)

