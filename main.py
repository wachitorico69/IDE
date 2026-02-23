from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QFrame
from PyQt5.uic import loadUi
import sys

# clase que hereda las propiedas de qmainwindow
class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        loadUi("main.ui", self) # carga main.ui en la clase
        self.current_path = None # para saber si es un archivo existente o nuevo
        self.current_fontSize = 10 # tam de la fuente
        initFont = self.textEdit.font()
        initFont.setPointSize(self.current_fontSize)
        self.textEdit.setFont(initFont)
        self.textEdit.setFrameShape(QFrame.NoFrame)
        self.setWindowTitle("IDE - Untitled") # nombre default

        # cursor
        self.textEdit.cursorPositionChanged.connect(self.update_cursor_position)
        self.update_cursor_position()

        # acciones y funciones para cada opción
        self.actionNew.triggered.connect(self.newFile)
        self.actionOpen.triggered.connect(self.openFile)
        self.actionSave.triggered.connect(self.saveFile)
        self.actionSave_As.triggered.connect(self.saveFileAs)
        self.actionClose.triggered.connect(self.closeFile)
        self.actionExit.triggered.connect(self.close)
        self.actionUndo.triggered.connect(self.undo)
        self.actionRedo.triggered.connect(self.redo)
        self.actionCut.triggered.connect(self.cut)
        self.actionCopy.triggered.connect(self.copy)
        self.actionPaste.triggered.connect(self.paste)
        self.actionDark_Theme.triggered.connect(self.setDarkTheme)
        self.actionLight_Theme.triggered.connect(self.setLightTheme)
        self.actionIncrease_font_size.triggered.connect(self.increaseFont)
        self.actionDecrease_Font_Size.triggered.connect(self.decreaseFont)

    def update_cursor_position(self):
        cursor = self.textEdit.textCursor() # obtener cursor actual
        line = cursor.blockNumber() + 1 # linea actual
        col = cursor.columnNumber() + 1 # columna

        self.statusBar().showMessage(f"Ln {line}, Col {col}") # mostrar

    # file
    def newFile(self):
        self.textEdit.clear()
        self.setWindowTitle("IDE - Untitled")
        self.current_path = None # no hay un archivo abierto
    
    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'All files (*.*)')
        
        if fileName:
            self.setWindowTitle("IDE - " + fileName) # agregar path del archivo al titulo
            with open(fileName, 'r') as f:
                fileText = f.read()
                self.textEdit.setPlainText(fileText) # mostrar el texto del archivo
            self.current_path = fileName # archivo abierto

    def saveFile(self):
        if self.current_path is not None:
            fileText = self.textEdit.toPlainText() 
            with open(self.current_path, 'w') as f:
                f.write(fileText) # escribir en el archivo
        else:
            self.saveFileAs() # guardar como si es un archivo nuevo

    def closeFile(self):
        # verificar si hay texto
        if self.textEdit.toPlainText() != "":
            respuesta = QMessageBox.question(
                self, 
                "Close File", 
                "Do you want to save the changes you made? Your changes will be lost if you don't save them.",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, 
                QMessageBox.Yes # no seleccionado por default
            )
            
            if respuesta == QMessageBox.Cancel:
                return
            elif respuesta == QMessageBox.No:
                # cerrar archivo
                self.textEdit.clear()
                self.current_path = None
                self.setWindowTitle("IDE - Untitled")
            else:
                self.saveFile()
                self.textEdit.clear()
                self.current_path = None
                self.setWindowTitle("IDE - Untitled")

    # función para exit o cuando se presiona la X de la ventana, dialogo de seguridad para el usuario
    def closeEvent(self, event):
        if self.textEdit.toPlainText() != "":
            respuesta = QMessageBox.question(
                self, 
                "Close IDE", 
                "Do you want to leave? Your changes will be lost if you don't save them.",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if respuesta == QMessageBox.Yes:
                event.accept() 
            else:
                event.ignore() 
        else:
            event.accept()

    def saveFileAs(self):
        pathName, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'Text files (*.*)')
        
        if pathName:
            fileText = self.textEdit.toPlainText()
            with open(pathName, 'w') as f:
                f.write(fileText)
            self.current_path = pathName
            self.setWindowTitle("IDE - " + pathName)

    # edit
    def undo(self):
        self.textEdit.undo()

    def redo(self):
        self.textEdit.redo()

    def cut(self):
        self.textEdit.cut()
    
    def copy(self):
        self.textEdit.copy()

    def paste(self):
        self.textEdit.paste()
    
    # view
    def setDarkTheme(self):
        self.setStyleSheet('''QWidget{
                           background-color: rgb(33,33,33);
                           color: #FFFFFF;
                           }
                           QPlaintTextEdit{
                           background-color: rgb(46,46,46);
                           border: none;
                           }
                           QMenuBar::item:selected{
                           color: #000000
                           } ''')

    def setLightTheme(self):
        self.setStyleSheet("") # string vacío que regresa el claro
    
    def increaseFont(self): 
        self.current_fontSize += 1
        font = self.textEdit.font()
        font.setPointSize(self.current_fontSize)
        self.textEdit.setFont(font)

    def decreaseFont(self):
        self.current_fontSize -= 1
        fuente = self.textEdit.font()
        fuente.setPointSize(self.current_fontSize)
        self.textEdit.setFont(fuente)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Main()
    ui.show()
    app.exec_()