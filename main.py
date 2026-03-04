from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QFrame, QDockWidget, QTextEdit, QToolBar, QStackedWidget, QVBoxLayout, QWidget, QAction, QMenu, QListWidget, QListWidgetItem
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
import sys
import os

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

        # =========================
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
        self.resizeDocks([self.terminalPanel], [160], Qt.Vertical)

        # ==========================================
        # LATERAL BAR (ACTIVITY BAR)
        # ==========================================
        self.opened_files_content = {} # diccionario para guardar el texto: {ruta: texto}
        
        # contenedor apilado
        self.stackedPanels = QStackedWidget()
        
        # explorador archivos
        self.panelArchivos = QListWidget()
        self.panelArchivos.setFrameShape(QFrame.NoFrame)
        self.panelArchivos.setStyleSheet("QListWidget { background-color: transparent; border: none; }")
        self.panelArchivos.itemClicked.connect(self.switchToFile) # click cambiar archivo
        
        # cerrar archivo click derecho
        self.panelArchivos.setContextMenuPolicy(Qt.CustomContextMenu)
        self.panelArchivos.customContextMenuRequested.connect(self.showFileContextMenu)
        
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

        self.stackedPanels.addWidget(self.panelArchivos)
        self.stackedPanels.addWidget(self.panelLexico)
        self.stackedPanels.addWidget(self.panelSintactico)
        self.stackedPanels.addWidget(self.panelSemantico)
        self.stackedPanels.addWidget(self.panelTabla)
        self.stackedPanels.addWidget(self.panelCodigo)

        self.sideBarDock = QDockWidget("Explorer", self)
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
        self.actArchivos = QAction("Archivos", self)
        self.actLexico = QAction("Léxico", self)
        self.actSintactico = QAction("Sintáctico", self)
        self.actSemantico = QAction("Semántico", self)
        self.actTabla = QAction("Tabla Símb.", self)
        self.actCodigo = QAction("Código Int.", self)

        # agregar botones a la barra
        self.activityBar.addAction(self.actArchivos)
        self.activityBar.addAction(self.actLexico)
        self.activityBar.addAction(self.actSintactico)
        self.activityBar.addAction(self.actSemantico)
        self.activityBar.addAction(self.actTabla)
        self.activityBar.addAction(self.actCodigo)

        self.actArchivos.triggered.connect(lambda: self.switchSidePanel(0, 'Explorer'))
        self.actLexico.triggered.connect(lambda: self.switchSidePanel(1, "Análisis Léxico"))
        self.actSintactico.triggered.connect(lambda: self.switchSidePanel(2, "Análisis Sintáctico"))
        self.actSemantico.triggered.connect(lambda: self.switchSidePanel(3, "Análisis Semántico"))
        self.actTabla.triggered.connect(lambda: self.switchSidePanel(4, "Tabla de Símbolos"))
        self.actCodigo.triggered.connect(lambda: self.switchSidePanel(5, "Código Intermedio"))

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
            # guardar el progreso del archivo q teníamos abierto actualmente
            if self.current_path:
                self.opened_files_content[self.current_path] = self.textEdit.toPlainText()

            # leer nuevo archivo
            with open(fileName, 'r') as f:
                fileText = f.read()
            
            # guardarlo en diccionario de memoria
            self.opened_files_content[fileName] = fileText
            
            # revisar si ya está en la lista o si no agregarlo
            items = self.panelArchivos.findItems(os.path.basename(fileName), Qt.MatchExactly)
            if not items:
                item = QListWidgetItem(os.path.basename(fileName)) # mostrar el nombre
                item.setData(Qt.UserRole, fileName) # guardar la ruta completa de forma invisible
                self.panelArchivos.addItem(item)
            
            # mostrar en editor
            self.textEdit.setPlainText(fileText)
            self.current_path = fileName
            self.setWindowTitle("IDE - " + fileName)
            
            # actualización del panel lateral para mostrar los archivos
            self.switchSidePanel(0, "Explorer")

    def saveFile(self):
        if self.current_path is not None:
            fileText = self.textEdit.toPlainText() 
            with open(self.current_path, 'w') as f:
                f.write(fileText) # escribir en el archivo
        else:
            self.saveFileAs() # guardar como si es un archivo nuevo

    def closeFile(self):
        # si hay texto preguntar para guardar
        if self.textEdit.toPlainText() != "":
            respuesta = QMessageBox.question(
                self, 
                "Close File", 
                "Do you want to save the changes you made? Your changes will be lost if you don't save them.",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, 
                QMessageBox.Yes 
            )
            
            if respuesta == QMessageBox.Cancel:
                return
            elif respuesta == QMessageBox.Yes:
                self.saveFile()

        # para limpiar lista del explorer
        if self.current_path:
            # quitar del diccionario
            if self.current_path in self.opened_files_content:
                del self.opened_files_content[self.current_path]
                
            # quitarlo del panel
            items = self.panelArchivos.findItems(os.path.basename(self.current_path), Qt.MatchExactly)
            for item in items:
                if item.data(Qt.UserRole) == self.current_path:
                    row = self.panelArchivos.row(item)
                    self.panelArchivos.takeItem(row)
                    break

        # cargar el siguiente archivo abierto o limpiar la pantalla
        self.current_path = None # Desvinculamos la ruta actual
        
        if self.panelArchivos.count() > 0:
            ultimo_item = self.panelArchivos.item(self.panelArchivos.count() - 1)
            self.switchToFile(ultimo_item)
        else:
            self.textEdit.clear()
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
        pathName, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'All files (*.*)')
        
        if pathName:
            fileText = self.textEdit.toPlainText()
            with open(pathName, 'w') as f:
                f.write(fileText)
                
            self.current_path = pathName
            self.setWindowTitle("IDE - " + pathName)

            self.opened_files_content[pathName] = fileText
            
            items = self.panelArchivos.findItems(os.path.basename(pathName), Qt.MatchExactly)
            if not items:
                item = QListWidgetItem(os.path.basename(pathName))
                item.setData(Qt.UserRole, pathName)
                self.panelArchivos.addItem(item)
                
            self.switchSidePanel(0, "Explorer")

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
        # mostrar panel si está oculto
        if not self.sideBarDock.isVisible():
            self.sideBarDock.show()
        
        # ocultar panel si se hace click en el botón del q se está mostrando
        elif self.stackedPanels.currentIndex() == index:
            self.sideBarDock.hide()
            return

        # cambiar panel y título al seleccionado
        self.stackedPanels.setCurrentIndex(index)
        self.sideBarDock.setWindowTitle(title)

    # =========================
    # FILE EXPLORER FUNCTIONS
    # =========================
    def switchToFile(self, item):
        # Obtener la ruta completa que guardamos de forma invisible
        clicked_path = item.data(Qt.UserRole) 
        
        # Si ya estamos en ese archivo, no hacemos nada
        if clicked_path == self.current_path: return
        
        # Guardar cambios del archivo que estamos a punto de abandonar
        if self.current_path:
            self.opened_files_content[self.current_path] = self.textEdit.toPlainText()
            
        # Cargar el contenido del archivo que le dimos click
        self.textEdit.setPlainText(self.opened_files_content.get(clicked_path, ""))
        self.current_path = clicked_path
        self.setWindowTitle("IDE - " + clicked_path)

    def showFileContextMenu(self, pos):
        # menú click derecho
        item = self.panelArchivos.itemAt(pos)
        if not item: return
        
        menu = QMenu()
        close_action = menu.addAction("Close File")
        action = menu.exec_(self.panelArchivos.mapToGlobal(pos))
        
        if action == close_action:
            self.closeFileFromExplorer(item)

    def closeFileFromExplorer(self, item):
        path_to_remove = item.data(Qt.UserRole)
        nombre_archivo = os.path.basename(path_to_remove)
        
        # preguntar por los cambios hechos (si es que hubo)
        respuesta = QMessageBox.question(
            self, 
            "Close File", 
            f"Do you want to save the changes to '{nombre_archivo}'?\nYour changes will be lost if you don't save them.",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, 
            QMessageBox.Yes 
        )
        
        # cancelar
        if respuesta == QMessageBox.Cancel:
            return
            
        # guardar
        elif respuesta == QMessageBox.Yes:
            if path_to_remove == self.current_path:
                # archivo activo
                fileText = self.textEdit.toPlainText()
            else:
                # archivo en segundo plano
                fileText = self.opened_files_content.get(path_to_remove, "")
                
            # sobrescribir
            with open(path_to_remove, 'w') as f:
                f.write(fileText)

        # se quita de la lista
        row = self.panelArchivos.row(item)
        self.panelArchivos.takeItem(row)
        
        # se quita del diccionario
        if path_to_remove in self.opened_files_content:
            del self.opened_files_content[path_to_remove]
            
        # si cierra un archivo
        if path_to_remove == self.current_path:            
            self.current_path = None 
            
            if self.panelArchivos.count() > 0:
                # último archivo de la lista y lo abrimos
                ultimo_item = self.panelArchivos.item(self.panelArchivos.count() - 1)
                self.switchToFile(ultimo_item)
            else:
                self.textEdit.clear()
                self.setWindowTitle("IDE - Untitled")
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
        quickBar = QToolBar("Quick Access", self.menuBar())
        quickBar.setMovable(False)
        quickBar.setFloatable(False)
        quickBar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        # FILE section
        quickBar.addAction(self.actionNew)
        quickBar.addAction(self.actionOpen)
        quickBar.addAction(self.actionSave)
        quickBar.addAction(self.actionSave_As)
        quickBar.addAction(self.actionClose)
        quickBar.addAction(self.actionExit)
        quickBar.addSeparator()  # |

        # EDIT section
        quickBar.addAction(self.actionUndo)
        quickBar.addAction(self.actionRedo)
        quickBar.addSeparator()  # |
        quickBar.addAction(self.actionCut)
        quickBar.addAction(self.actionCopy)
        quickBar.addAction(self.actionPaste)
        quickBar.addSeparator()  # |

        # VIEW section
        quickBar.addAction(self.actionDark_Theme)
        quickBar.addAction(self.actionLight_Theme)
        quickBar.addSeparator()  # |
        quickBar.addAction(self.actionIncrease_font_size)
        quickBar.addAction(self.actionDecrease_Font_Size)
        quickBar.addSeparator()  # |
        quickBar.addAction(self.actionTerminal)
        quickBar.addSeparator()  # |

        # COMPILAR section
        quickBar.addAction(self.actionL_xico)
        quickBar.addAction(self.actionSint_ctico)
        quickBar.addAction(self.actionSem_ntico)
        quickBar.addSeparator()  # |
        quickBar.addAction(self.actionGenerar_c_digo_intermedio)
        quickBar.addSeparator()  # |
        quickBar.addAction(self.actionEjecutar)

        # tamaño de los iconos
        quickBar.setIconSize(QSize(16, 16))
        self.addToolBar(Qt.TopToolBarArea, quickBar)


# =========================
# START APPLICATION
# =========================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Main()
    ui.showMaximized()
    app.exec_()