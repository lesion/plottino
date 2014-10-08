#!/usr/bin/env python
"""
Plottino 0.1
lowtech labs.

"""
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.Qwt5 as Qwt
import producers
import sys
from time import sleep

class Plottino(QMainWindow):

    def __init__(self, parent=None):

        QMainWindow.__init__( self, parent )

        #curves
        self.curves = []

        # data of curves
        self.data = []

        self.pause = None

        self.wavailable_producers=None
        self.wused_producers=None
        self.used_producers=[]

        self.create_main_frame()


    def create_main_frame( self ):

        """ create main frame """
        self.main_frame = QWidget()
        main_layout = QGridLayout()
        main_layout.addWidget(self.create_controls(),0,0,1,0)
        main_layout.addWidget(self.create_plot(),1,0)
        main_layout.addWidget(self.create_producers(),1,1)
        main_layout.addWidget(self.create_status_bar(),2,0,1,0)

        main_layout.setColumnMinimumWidth(0,800)
        self.main_frame.setMinimumSize(900,600)
        self.main_frame.setLayout(main_layout)
        self.setCentralWidget(self.main_frame)


    def create_status_bar(self):
        status_bar = QWidget()
        layout = QHBoxLayout()

        max_items = QSlider(Qt.Horizontal,status_bar)

        max_items.setMinimum(10)
        max_items.setMaximum(5000)
        max_items.valueChanged.connect(self.set_max_items)

        layout.addWidget(max_items)
        status_bar.setLayout(layout)
        return status_bar


    def set_max_items(self,value):
        self.plot.setAxisScale(Qwt.QwtPlot.xBottom, 0, value)
        self.plot.replot()


    def create_producers(self):
        wproducers = QWidget()
        wproducers.setMaximumWidth(250)
        layout = QVBoxLayout()

        self.wavailable_producers = QListWidget(self)
        self.wused_producers = QListWidget(self)

        self.wavailable_producers.itemDoubleClicked.connect(self.addProducer)

        for producer in dir(producers):
            if producer=='os' or producer[0]=='_':
                continue
            self.wavailable_producers.addItem(producer)

        layout.addWidget(self.wavailable_producers)
        layout.addWidget(self.wused_producers)

        wproducers.setLayout(layout)

        return wproducers


    def addProducer(self,producer):
        producer_name = producer.text()
        self.wused_producers.addItem(producer_name)

        # load the producer and set preferences
        new_data = [[],[]]
        self.data.append(new_data)
        new_producer = getattr(producers,str(producer_name)).Producer(self,new_data)
        self.used_producers.append(new_producer)
        new_producer.openPreference(self)

        # create a new graph for this producer and attach to the plot
        new_curve = Qwt.QwtPlotCurve('')
        self.curves.append( new_curve )
        #new_curve.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)
        new_curve.setCurveType( Qwt.QwtPlotCurve.Yfx )
        new_curve.setYAxis( Qwt.QwtPlot.yLeft )
        pen = QPen(QColor(len(self.curves)*50,100,200))
        #new_curve.setCurveFitter( Qwt.QwtSplineCurveFitter() )
        pen.setWidth(1)
        new_curve.setPen(pen)
        new_curve.attach(self.plot)

        #new_curve.setCurveAttribute(Qwt.QwtPlotCurve.Fitted,True);
        new_curve.setStyle( Qwt.QwtPlotCurve.Lines )
        #fit = Qwt.QwtWeedingCurveFitter(1)
        #fit.setSplineSize( 120 )
        #new_curve.setCurveFitter( fit );

    def removeProducer(self):
        print "Dentro remove producer"

    def create_controls( self ):
        controls = QWidget()
        layout = QHBoxLayout()

        self.start_button = QPushButton( QIcon.fromTheme( 'media-playback-start' ), "Start" )
        self.start_button.setCheckable( True )
        self.start_button.clicked.connect(self.start)
        layout.addWidget( self.start_button )


        screenshoot = QPushButton( QIcon.fromTheme( 'camera-photo' ), "Screenshoot" )
        self.connect( screenshoot, SIGNAL("clicked()"), self.screenshoot )
        layout.addWidget( screenshoot )

        controls.setLayout( layout )
        return controls


    def create_plot( self ):
        plot = Qwt.QwtPlot(self)
        plot.setCanvasBackground(Qt.black)
        plot.setAxisTitle(Qwt.QwtPlot.xBottom, 'Time')
        plot.enableAxis( Qwt.QwtPlot.yLeft, True )
        zoomer = Qwt.QwtPlotMagnifier( plot.canvas() )
        zoomer.setAxisEnabled(Qwt.QwtPlot.xBottom,False )
        self.plot = plot
        return plot


    def screenshoot( self ):
        self.pause = True

        fileName = QFileDialog.getSaveFileName( self, "Select filename", "", "Images (*.png)" )
        pixmap = QPixmap.grabWidget(self.plot)

        if ( pixmap.save(fileName, "png" )):
            self.status.setText( "Saved to %s" % fileName )
        else:
            self.status.setText( "Error!!" )

        self.pause = False


    def start(self):
        if self.pause==False:
            for t in self.used_producers:
              t.pause=True
            self.pause=True
            self.start_button.setIcon(QIcon.fromTheme("media-playback-start"))
            return
        elif self.pause==True:
            for t in self.used_producers:
              t.pause=False
            self.pause=False
            self.start_button.setIcon(QIcon.fromTheme("media-playback-pause"))
            return

        self.start_button.setIcon(QIcon.fromTheme("media-playback-pause"))
        #start threads
        for t in self.used_producers:
            print "Start thread " , t
            t.init()
            t.start()

        self.pause=False
        while True:
            if self.pause:
                QApplication.processEvents()
                sleep(0.1)
                continue

            i = 0
            max_x = 0
            min_x = None
            for t in self.used_producers:
                min_x = t.min_x if min_x==None or min_x>t.min_x else min_x
                max_x = t.max_x if max_x<t.max_x else max_x

                self.curves[i].setData(t.data[0], t.data[1])
                i+=1

            self.plot.setAxisScale(Qwt.QwtPlot.xBottom, min_x, max_x )
            self.plot.replot()
            QApplication.processEvents()



def main():
    app = QApplication(sys.argv)
    win = Plottino()
    win.show()
    app.exec_()


if __name__ == "__main__":
    main()
