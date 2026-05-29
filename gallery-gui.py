import sys
from os import listdir
from pathlib import Path
from time import sleep, time

from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMenuBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QToolButton,
    QScrollArea
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gallery")

        self.PickPath = QAction("Pick Path", self)
        self.Rescan = QAction("Rescan Path", self)
        self.Information = QAction("Information About Image", self)
        self.randomwidget = QWidget(self)
        self.BackButton = QAction("Back", self)
        self.PathLabel = QAction("",self)
        self.PathLabel.setEnabled(False)
        self.scrollarea = QScrollArea(self)
        self.scrollarea.setWidgetResizable(True)
        self.resize(550,400)
        self.setCentralWidget(self.randomwidget)
        self.initUI()
        self.menubarlist()
        
        self.Start = True

    def initUI(self):

        self.menubarwidget = QWidget(self.randomwidget)
        self.widget = QWidget(self.randomwidget)

        self.MainBoxLayout = QVBoxLayout()

        self.MainBoxLayout.addWidget(self.menubarwidget)
        self.MainBoxLayout.addWidget(self.scrollarea)
        self.randomwidget.setLayout(self.MainBoxLayout)
        
        self.GridLayout = QGridLayout()
        self.widget.setLayout(self.GridLayout)
        
        self.menubarwidget.setFixedSize(400,40)

    def menubarlist(self):
        self.menubar = QMenuBar(self.menubarwidget)
        self.menubar.setFixedSize(400,40)
        
        self.FirstMenu = self.menubar.addMenu("Paths")
        self.FirstMenu.addAction(self.PickPath)
        self.FirstMenu.addAction(self.Rescan)
        self.FirstMenu.addAction(self.Information)
        
        self.Back = self.menubar.addAction(self.BackButton)
        
        self.label = self.menubar.addAction(self.PathLabel)
        
        self.PickPath.triggered.connect(self.selectfolder)
        self.Rescan.triggered.connect(self.Scan)
        self.BackButton.triggered.connect(self.back)
    
    def back(self):
        if not hasattr(self, "basedir"):
            return
        else:
            pathtogo = self.basedir.rsplit("/",1)[0]
            
            if len(pathtogo) < len(self.StartingPath):
                return
            else:
                self.cleanwidgets(self.GridLayout)
                self.Scan(pathtogo)
    
    def selectfolder(self):
        self.FileWindow = QFileDialog(self)
        self.FileWindow.setFileMode(QFileDialog.FileMode.Directory)
        self.FileWindow.show()
        if self.FileWindow.exec():
            self.PathToScan = self.FileWindow.selectedFiles()
            self.cleanwidgets(self.GridLayout)
            self.Scan(self.PathToScan[0])

    def Scan(self, SomeDir):
        DirsToScan = set()
        ScannedDirs = set()
        Images = set()
        basedir = SomeDir
        FirstRun = True

        self.PathLabel.setText(basedir)
        
        global path

        path = basedir

        def addimages(folders):
            if not folders.endswith("/"):
                folders += "/"
            for files in listdir(folders):
                if "." in files[0]:
                    continue
                if (
                    not Path.is_dir(folders + files)
                    and not Path.is_symlink(folders + files)
                    and files.endswith((".png", ".jpeg", ".jpg", ".webp"))
                ):
                    Images.add(folders + files)

            if folders is not basedir:
                ScannedDirs.add(folders)

        def checkdirs(folders):
            if not folders.endswith("/"):
                folders += "/"
            for files in listdir(folders):
                if "." in files[0]:
                    continue
                if Path.is_dir(folders + files) and not Path.is_symlink(
                    folders + files
                ):
                    DirsToScan.add(folders + files)

        def changedirs(folders):
            if not folders.endswith("/"):
                folders += "/"
            global path
            DirsAvail = []
            for files in listdir(folders):  # Get the list of directories
                if "." in files[0]:
                    continue
                if Path.is_dir(folders + files) and not Path.is_symlink(
                    folders + files
                ):
                    DirsAvail.append(folders + files + "/")

            for Dirs in DirsAvail:
                if Dirs not in ScannedDirs and not Path.is_symlink(Dirs):
                    path = Dirs
                    return

        def getout(folders):
            self.resize(400,400)
            if not folders.endswith("/"):
                folders += "/"
            global path
            dirs = []

            for dir in listdir(folders):
                if "." in dir[0]:
                    continue
                if Path.is_dir(folders + dir) and not Path.is_symlink(folders + dir):
                    dirs.append(folders + dir + "/")

            if dirs == []:
                if basedir not in folders.rsplit("/", 2)[0]:
                    return
                path = folders.rsplit("/", 2)[0]
                return

            for stuff in dirs:
                if stuff not in ScannedDirs:
                    return

                if basedir not in folders.rsplit("/", 2)[0]:
                    return
                path = folders.rsplit("/", 2)[0]
                return

            for stuff in dirs:
                if stuff in ScannedDirs:
                    if basedir not in folders.rsplit("/", 2)[0]:
                        return
                    path = folders.rsplit("/", 2)[0]
                    return

        checkdirs(path)

        benchmarktimestart = time()
        
        while len(DirsToScan) > len(ScannedDirs) or FirstRun:
            addimages(path)
            getout(path)
            checkdirs(path)
            changedirs(path)
            FirstRun = False
        benchmarktimestop = time()

        if self.Start:
            self.StartingPath = basedir
            self.Start = False
        
        self.benchmarktime = (benchmarktimestop - benchmarktimestart) * 1000

        self.ScannedDirs = ScannedDirs
        self.Images = Images
        self.basedir = basedir
        self.menubar.setFixedWidth(self.width())
        self.ShowImages()

    def ShowImages(self):

        ImagePerFolder = set()
        imagesincurdir = set()
        for a in self.Images:
            folders = a.split(self.basedir)[1].split("/", 2)[1]
            folders = self.basedir + "/" + folders
            if Path.is_dir(folders):
                ImagePerFolder.add(folders.rsplit("/", 1)[1])
            for dir in listdir(self.basedir):
                if (
                    not Path.is_dir(dir)
                    and not Path.is_symlink(dir)
                    and dir.endswith((".png", ".webp", ".jpg", ".jpeg"))
                ):
                    imagesincurdir.add(dir)

        row = 0
        collumn = 0
        for ImagesInFolder in ImagePerFolder:
            icon = QIcon()
            for image in self.Images:
                if ImagesInFolder in image:
                    icon = QIcon(image)
            buttons = QToolButton(self.widget)
            buttons.setText(ImagesInFolder)
            buttons.setIcon(icon)
            buttons.setIconSize(QSize(80, 80))
            buttons.setFixedSize(110,110)
            buttons.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            buttons.released.connect(
                lambda DirToGo=ImagesInFolder: self.changedir(DirToGo)
            )
            self.GridLayout.addWidget(buttons, row, collumn)
            collumn += 1
            if collumn == 4:
                row += 1
                collumn = 0

        for ImageInCurrentFolder in imagesincurdir:
            icon = QIcon(self.basedir + "/" + ImageInCurrentFolder)
            button = QPushButton("", self.widget)
            button.setIcon(icon)
            button.setIconSize(QSize(80, 80))
            button.setFixedSize(110,110)
            button.released.connect(
                lambda road=self.basedir + "/" + ImageInCurrentFolder: (
                    self.creatingsecondwindow(road)
                )
            )
            self.GridLayout.addWidget(button, row, collumn)
            collumn += 1
            if collumn == 4:
                row += 1
                collumn = 0

        self.widget.setStyleSheet("QPushButton{text-align:bottom;}")
        self.scrollarea.setWidget(self.widget)
        self.resize(550,400)
        

    def cleanwidgets(self, widget):
        for widgetcount in reversed(range(widget.count())):
            widget.itemAt(widgetcount).widget().setParent(None)

    def changedir(self, DirToGo):
        self.cleanwidgets(self.GridLayout)
        self.Scan(self.basedir + "/" + DirToGo)

    def creatingsecondwindow(self, path):
        self.Image = Image(path)
        self.Image.show()


class Image(QWidget):
    def __init__(self, path):
        super().__init__()
        self.setMaximumSize(QApplication.primaryScreen().size()/1.5)
        self.ImageLabel = QLabel(self)

        self.PixMap = QPixmap(path)

        self.Width = self.PixMap.width()
        self.Height = self.PixMap.height()

        self.setWindowTitle(f"{path.rsplit('/', 1)[1]} Res: {self.Width}x{self.Height}")

        self.ImageLabel.setPixmap(self.PixMap)
        self.ImageLabel.setScaledContents(True)
        self.ImageLabel.resize(self.Width, self.Height)
        self.ImageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def resizeEvent(self, a0):
        sleep(0.01)
        WindowWidth = a0.size().width()
        WindowHeight = a0.size().height()
        self.ImageLabel.resize(WindowWidth, WindowHeight)


def main():
    app = QApplication(sys.argv)
    gallerymw = MainWindow()
    gallerymw.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
