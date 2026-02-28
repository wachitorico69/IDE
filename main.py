from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QFrame, QDockWidget, QTextEdit, QToolBar, QStackedWidget, QVBoxLayout, QWidget, QAction
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
import sys

# clase que hereda las propiedas de qmainwindow
class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        loadUi("main.ui", self) # carga main.ui en la clase
        # =========================
        # VARIABLES
        # =========================
        self.current_path = None # para saber si es un archivo existente o nuevo
        self.current_fontSize = 10 # tam de la fuente
        # =========================
        # EDITOR INITIAL SETUP
        # =========================
        initFont = self.textEdit.font()
        initFont.setPointSize(self.current_fontSize)
        self.textEdit.setFont(initFont)
        self.textEdit.setFrameShape(QFrame.NoFrame)
        self.setWindowTitle("IDE - Untitled") # nombre default

        # cursor
        self.textEdit.cursorPositionChanged.connect(self.update_cursor_position)
        self.update_cursor_position()

           # =========================
        # FILE ACTIONS
        # =========================
        self.actionNew.triggered.connect(self.newFile)
        self.actionOpen.triggered.connect(self.openFile)
        self.actionSave.triggered.connect(self.saveFile)
        self.actionSave_As.triggered.connect(self.saveFileAs)
        self.actionClose.triggered.connect(self.closeFile)
        self.actionExit.triggered.connect(self.close)

        # =========================
        # EDIT ACTIONS
        # =========================
        self.actionUndo.triggered.connect(self.textEdit.undo)
        self.actionRedo.triggered.connect(self.textEdit.redo)
        self.actionCut.triggered.connect(self.textEdit.cut)
        self.actionCopy.triggered.connect(self.textEdit.copy)
        self.actionPaste.triggered.connect(self.textEdit.paste)

        # =========================
        # VIEW ACTIONS
        # =========================
        self.actionDark_Theme.triggered.connect(self.setDarkTheme)
        self.actionLight_Theme.triggered.connect(self.setLightTheme)
        self.actionIncrease_font_size.triggered.connect(self.increaseFont)
        self.actionDecrease_Font_Size.triggered.connect(self.decreaseFont)
        self.actionTerminal.triggered.connect(self.showTerminal)

        # =========================
        # BUILD & DEBUG ACTIONS
        # =========================
        self.actionBuildProject.triggered.connect(self.buildProject)
        self.actionRebuild.triggered.connect(self.rebuild)
        self.actionClean.triggered.connect(self.clean)
        self.actionBuildSolution.triggered.connect(self.buildSolution)

        self.actionStartDebugging.triggered.connect(self.runFile)
        self.actionStartWithoutDebugging.triggered.connect(self.runFile)
        self.actionStopDebugging.triggered.connect(self.stopExecution)
        self.actionRestartDebugging.triggered.connect(self.restartExecution)
        self.actionAttachProcess.triggered.connect(self.attachProcess)

        # ==========================================
        # TERMINAL
        # ==========================================
        self.terminalPanel = QDockWidget("Terminal", self)
        self.terminalPanel.setAllowedAreas(Qt.BottomDockWidgetArea) # anclada en la parte de abajo
        
        self.terminalOutput = QTextEdit()
        self.terminalOutput.setReadOnly(True) # lectura pq solo muestra mensajes
        
        self.terminalOutput.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                color: #000000;
                font-family: Consolas, monospace;
                font-size: 10pt;
                border: none;
            }
        """)
        
        self.terminalPanel.setWidget(self.terminalOutput)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.terminalPanel)

        # ==========================================
        # LATERAL BAR (ACTIVITY BAR)
        # ==========================================
        
        # contenedor apilado
        self.stackedPanels = QStackedWidget()
        
        # área de texto para cada opción
        self.panelLexico = QTextEdit()
        self.panelLexico.setReadOnly(True)
        self.panelLexico.setFrameShape(QFrame.NoFrame)
        self.panelLexico.setPlainText("Análisis Léxico...")
        
        self.panelSintactico = QTextEdit()
        self.panelSintactico.setReadOnly(True)
        self.panelSintactico.setFrameShape(QFrame.NoFrame)
        self.panelSintactico.setPlainText("Análisis Sintáctico...")

        self.panelSemantico = QTextEdit()
        self.panelSemantico.setReadOnly(True)
        self.panelSemantico.setFrameShape(QFrame.NoFrame)
        self.panelSemantico.setPlainText("Análisis Semántico...")

        self.panelTabla = QTextEdit()
        self.panelTabla.setReadOnly(True)
        self.panelTabla.setFrameShape(QFrame.NoFrame)
        self.panelTabla.setPlainText("Tabla de Símbolos...")

        self.panelCodigo = QTextEdit()
        self.panelCodigo.setReadOnly(True)
        self.panelCodigo.setFrameShape(QFrame.NoFrame)
        self.panelCodigo.setPlainText("Código Intermedio...")

        self.stackedPanels.addWidget(self.panelLexico)
        self.stackedPanels.addWidget(self.panelSintactico)
        self.stackedPanels.addWidget(self.panelSemantico)
        self.stackedPanels.addWidget(self.panelTabla)
        self.stackedPanels.addWidget(self.panelCodigo)

        self.sideBarDock = QDockWidget("Análisis Léxico", self)
        self.sideBarDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.sideBarDock.setWidget(self.stackedPanels)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sideBarDock)

        # barra de botones vertical
        self.activityBar = QToolBar("Barra de Actividades")
        self.activityBar.setMovable(False) 
        self.addToolBar(Qt.LeftToolBarArea, self.activityBar)

        self.activityBar.setStyleSheet("""
            QToolBar {
                border: none;
                background: transparent;
            }
            QToolButton {
                min-width: 80px; 
                max-width: 80px;
                padding: 6px;
                font-size: 13px;
                border: 1px solid #c0c0c0; 
                background-color: #f8f9fa; 
            }
            QToolButton:hover {
                background-color: #e2e6ea; 
                border: 1px solid #a0a0a0;
            }
            QToolButton:pressed {
                background-color: #dae0e5; 
            }
        """)
        
        self.addToolBar(Qt.LeftToolBarArea, self.activityBar)

        # acciones de botones
        self.actLexico = QAction("Léxico", self)
        self.actSintactico = QAction("Sintáctico", self)
        self.actSemantico = QAction("Semántico", self)
        self.actTabla = QAction("Tabla Símb.", self)
        self.actCodigo = QAction("Código Int.", self)

        # agregar botones a la barra
        self.activityBar.addAction(self.actLexico)
        self.activityBar.addAction(self.actSintactico)
        self.activityBar.addAction(self.actSemantico)
        self.activityBar.addAction(self.actTabla)
        self.activityBar.addAction(self.actCodigo)

        self.actLexico.triggered.connect(lambda: self.switchSidePanel(0, "Análisis Léxico"))
        self.actSintactico.triggered.connect(lambda: self.switchSidePanel(1, "Análisis Sintáctico"))
        self.actSemantico.triggered.connect(lambda: self.switchSidePanel(2, "Análisis Semántico"))
        self.actTabla.triggered.connect(lambda: self.switchSidePanel(3, "Tabla de Símbolos"))
        self.actCodigo.triggered.connect(lambda: self.switchSidePanel(4, "Código Intermedio"))

        self.setLightTheme()      

    # =========================
    # STATUS BAR FUNCTION
    # =========================
    def update_cursor_position(self):
        cursor = self.textEdit.textCursor() # obtener cursor actual
        line = cursor.blockNumber() + 1 # linea actual
        col = cursor.columnNumber() + 1 # columna

        self.statusBar().showMessage(f"Ln {line}, Col {col}") # mostrar

    # =========================
    # FILE FUNCTIONS
    # =========================
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
    
    # =========================
    # VIEW FUNCTIONS
    # =========================
    def setDarkTheme(self):
        self.setStyleSheet('''
            QWidget {
                background-color: rgb(33,33,33);
                color: #FFFFFF;
            }
            QPlainTextEdit, QTextEdit { 
                background-color: rgb(46,46,46);
                border: none;
                outline: none; 
            }
            QMenuBar {
                background-color: rgb(33,33,33);
            }
            QMenuBar::item {
                padding: 5px 12px; 
                border-right: 1px solid #555555; 
            }
            QMenuBar::item:selected {
                background-color: rgb(60,60,60); 
            } 
            QMenu {
                background-color: rgb(46,46,46); 
                border: 1px solid #555555; 
            }
            QMenu::item:selected {
                background-color: rgb(60,60,60);
            }
        ''')
        self.activityBar.setStyleSheet("""
            QToolBar {
                border: none;
                background: transparent;
            }
            QToolButton {
                min-width: 80px; 
                max-width: 80px;
                padding: 6px;
                font-size: 13px;
                border: 1px solid #c0c0c0; 
                background-color: rgb(33,33,33);
            }
            QToolButton:hover {
                background-color: rgb(60,60,60); 
                border: 1px solid #a0a0a0;
            }
            QToolButton:pressed {
                background-color: #dae0e5; 
            }
        """)
        self.terminalOutput.setStyleSheet("""
            QTextEdit {
                background-color: rgb(33,33,33);
                color: #ffffff;
                font-family: Consolas, monospace;
                font-size: 10pt;
                border: none;
            }
        """)

    def setLightTheme(self):
        self.setStyleSheet('''
            QMenuBar::item {
                padding: 5px 12px;
                border-right: 1px solid #cccccc; 
            }
            QMenuBar::item:selected {
                background-color: #e0e0e0;
            } 
        ''')
        self.activityBar.setStyleSheet("""
            QToolBar {
                border: none;
                background: transparent;
            }
            QToolButton {
                min-width: 80px; 
                max-width: 80px;
                padding: 6px;
                font-size: 13px;
                border: 1px solid #c0c0c0; 
                background-color: #f8f9fa; 
            }
            QToolButton:hover {
                background-color: #e2e6ea; 
                border: 1px solid #a0a0a0;
            }
            QToolButton:pressed {
                background-color: #dae0e5; 
            }
        """)
        
        self.terminalOutput.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                color: #000000;
                font-family: Consolas, monospace;
                font-size: 10pt;
                border: none;
            }
        """)
    
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

    def showTerminal(self):
        if self.terminalPanel.isVisible():
            self.terminalPanel.hide()
        else:
            self.terminalPanel.show()

    def switchSidePanel(self, index, title):
        # Si el panel está oculto, lo mostramos primero
        if not self.sideBarDock.isVisible():
            self.sideBarDock.show()
        
        # Si hacemos clic en el botón del panel que YA estamos viendo, lo ocultamos (estilo VS Code)
        elif self.stackedPanels.currentIndex() == index:
            self.sideBarDock.hide()
            return

        # Cambiamos a la vista seleccionada y actualizamos el título del panel
        self.stackedPanels.setCurrentIndex(index)
        self.sideBarDock.setWindowTitle(title)

 # =========================
    # BUILD (No funciona)
    # =========================
    def buildProject(self):
        self.statusBar().showMessage("Building project...")

    def rebuild(self):
        self.statusBar().showMessage("Rebuilding project...")

    def clean(self):
        self.statusBar().showMessage("Cleaning project...")

    def buildSolution(self):
        self.statusBar().showMessage("Building solution...")


    # =========================
    # DEBUG / RUN SYSTEM
    # =========================
    def runFile(self):
        if not self.current_path:
            QMessageBox.warning(self, "Error", "Please save the file before running.")
            return

        self.statusBar().showMessage("Running...")
        self.process.start("python", [self.current_path])

    def stopExecution(self):
        self.process.kill()
        self.statusBar().showMessage("Execution stopped.")

    def restartExecution(self):
        self.stopExecution()
        self.runFile()

    def attachProcess(self):
        QMessageBox.information(self, "Attach Process", "Feature not implemented yet.")


# =========================
# START APPLICATION
# =========================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Main()
    ui.showMaximized()
    app.exec_()