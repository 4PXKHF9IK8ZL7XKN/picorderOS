#/bin/python3
import sys

from PyQt6.QtWidgets import QLabel, QLineEdit, QGridLayout, QFormLayout, QGraphicsProxyWidget, QGraphicsItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView, QToolBar, QWidget, QVBoxLayout, QApplication, QMainWindow, QTabWidget, QPushButton, QLCDNumber, QStylePainter

from PyQt6.QtGui import QColor

from layout_colorwidget import Color

class costume_tab_widget(QTabWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
    def addTab_rotatet(self,layout,name):
        self.addTab(layout,name)
        print(name)

class tab_form_widget(QWidget):
    def __init__(self, parent):
        #super().__init__()
        super(QWidget, self).__init__(parent)
        #background = (245, 245, 245)

        #main_layout = QGridLayout(self)
        #self.setLayout(main_layout)

        contact_layout = QFormLayout()
        personal_layout = QFormLayout()


        tab = costume_tab_widget(self)
        tab.resize(600,400)

        tab.setTabPosition(QTabWidget.TabPosition.West)

        contact_page = QWidget(self)
        contact_page.setLayout(contact_layout)
        contact_layout.addRow('First Name:', QLineEdit(self))
        #contact_layout.setBackground("blue")


        personal_page = QWidget(self)
        personal_page.setLayout(personal_layout)
        personal_layout.addRow('Phone Number:', QLineEdit(self))


        tab.addTab_rotatet(personal_page, 'Personal Info')
        tab.addTab_rotatet(contact_page, 'Contact Info')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LCARS")
        self.showFullScreen()

        #scene = QGraphicsScene(0, 0, 400, 200)

        #rect = QGraphicsRectItem(0, 0, 200, 50)
        #rect.setPos(50, 20)

        #scene.addItem(rect)

        #view = QGraphicsView(scene)
        #view.show()

        self.table_widget = tab_form_widget(self)

        self.setCentralWidget(self.table_widget)

        self.show()


if __name__ == "__main__":
    # You need one (and only one) QApplication instance per application.
    # Pass in sys.argv to allow command line arguments for your app.
    # If you know you won't use command line arguments QApplication([]) works too.
    app = QApplication(sys.argv)

    # Create a Qt widget, which will be our window.
    window = MainWindow()

    window.show() # IMPORTANT!!!!! Windows are hidden by default.
    # Start the event loop.
    sys.exit(app.exec())
