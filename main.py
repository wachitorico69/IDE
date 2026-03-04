from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QFrame, QDockWidget, QTextEdit, QToolBar, QStackedWidget, QVBoxLayout, QWidget, QAction
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
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
        fuente_editor = QFont("Consolas", self.current_fontSize)
        self.textEdit.document().setDefaultFont(fuente_editor) 
        self.textEdit.setFont(fuente_editor) 
        self.textEdit.setFrameShape(QFrame.NoFrame)

        self.textEdit.updateLineNumberAreaWidth(0) # soluciona overlap del editor y barra de numeros

        self.setWindowTitle("IDE - Untitled")

        # cursor
        self.textEdit.cursorPositionChanged.connect(self.update_cursor_position)
        self.update_cursor_position()

        #iconos
        self.setup_icons()

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
                min-width: 55px; 
                max-width: 55px;
                padding: 6px;
                font-size: 10px;
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
                min-width: 55px; 
                max-width: 55px;
                padding: 6px;
                font-size: 10px;
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
                min-width: 55px; 
                max-width: 55px;
                padding: 6px;
                font-size: 10px;
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
        font = QFont("Consolas", self.current_fontSize)
        self.textEdit.document().setDefaultFont(font)
        self.textEdit.setFont(font)

    def decreaseFont(self):
        self.current_fontSize -= 1
        font = QFont("Consolas", self.current_fontSize)
        self.textEdit.document().setDefaultFont(font)
        self.textEdit.setFont(font)

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

    #metodo para agregar iconos
    def setup_icons(self):
        style = self.style()

        # iconos en FILE
        self.actionNew.setIcon(style.standardIcon(style.SP_FileIcon))
        self.actionOpen.setIcon(style.standardIcon(style.SP_DirIcon))
        self.actionSave.setIcon(style.standardIcon(style.SP_DialogSaveButton))
        self.actionSave_As.setIcon(style.standardIcon(style.SP_DriveFDIcon))
        self.actionClose.setIcon(style.standardIcon(style.SP_DialogCloseButton))
        self.actionExit.setIcon(style.standardIcon(style.SP_TitleBarCloseButton))

        # Iconos en Menu
        self.actionUndo.setIcon(style.standardIcon(style.SP_ArrowBack))
        self.actionRedo.setIcon(style.standardIcon(style.SP_ArrowForward))
        self.actionCut.setIcon(style.standardIcon(style.SP_DialogResetButton))
        self.actionCopy.setIcon(style.standardIcon(style.SP_FileDialogContentsView))
        self.actionPaste.setIcon(style.standardIcon(style.SP_FileDialogDetailedView))

        # Iconos en Vista
        self.actionDark_Theme.setIcon(style.standardIcon(style.SP_DesktopIcon))
        self.actionLight_Theme.setIcon(style.standardIcon(style.SP_DesktopIcon))
        self.actionIncrease_font_size.setIcon(style.standardIcon(style.SP_ArrowUp))
        self.actionDecrease_Font_Size.setIcon(style.standardIcon(style.SP_ArrowDown))
        self.actionTerminal.setIcon(style.standardIcon(style.SP_ComputerIcon))

        #Iconos en Compilar
        self.actionL_xico.setIcon(style.standardIcon(style.SP_FileDialogContentsView))
        self.actionSint_ctico.setIcon(style.standardIcon(style.SP_FileDialogListView))
        self.actionSem_ntico.setIcon(style.standardIcon(style.SP_FileDialogDetailedView))
        self.actionGenerar_c_digo_intermedio.setIcon(style.standardIcon(style.SP_FileDialogNewFolder))
        self.actionEjecutar.setIcon(style.standardIcon(style.SP_MediaPlay))

        #Iconos apareciendo en el ToolBar
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.toolBar.addAction(self.actionNew)
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addAction(self.actionSave)
        self.menuBar().setCornerWidget(self.toolBar, Qt.TopRightCorner) 


# =========================
# START APPLICATION
# =========================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Main()
    ui.showMaximized()
    app.exec_()