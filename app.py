import sys
from pathlib import Path

from PyQt6.QtGui import QCloseEvent, QIcon, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMessageBox,
)

from principal import Ui_MainWindow
from gramatica import ErrorEjecucion, ejecutar, lexer, parser


EXTENSION_POR_DEFECTO = ".ism"
FILTRO_ARCHIVOS = "Archivos ISM (*.ism);;Archivos de texto (*.txt);;Todos los archivos (*)"


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.current_file: Path | None = None
        self.recent_files: list[Path] = []

        image_dir = Path(__file__).resolve().parent / "Images"
        for action, icon_file in (
            (self.action_New, "file-new.png"),
            (self.action_Open, "file-open.png"),
            (self.action_Save, "file-save.png"),
            (self.action_Exit, "file-exit.png"),
            (self.action_Copy, "edit-copy.png"),
            (self.action_Paste, "edit-paste.png"),
            (self.action_Cut, "edit-cut.png"),
            (self.action_Acerca_de, "help-content.png"),
        ):
            action.setIcon(QIcon(str(image_dir / icon_file)))

        self.action_New.setShortcut(QKeySequence.StandardKey.New)
        self.action_Open.setShortcut(QKeySequence.StandardKey.Open)
        self.action_Save.setShortcut(QKeySequence.StandardKey.Save)
        self.action_Copy.setShortcut(QKeySequence.StandardKey.Copy)
        self.action_Cut.setShortcut(QKeySequence.StandardKey.Cut)
        self.action_Paste.setShortcut(QKeySequence.StandardKey.Paste)
        self.action_Find_and_Replace.setShortcut(QKeySequence.StandardKey.Find)
        self.actionOpen_Recent.setEnabled(False)

        self.action_New.triggered.connect(self.nuevo_archivo)
        self.action_Open.triggered.connect(self.abrir_archivo)
        self.actionOpen_Recent.triggered.connect(self.abrir_reciente)
        self.action_Save.triggered.connect(self.guardar_archivo)
        self.action_Exit.triggered.connect(self.close)
        self.action_Copy.triggered.connect(self.cajaTexto.copy)
        self.action_Cut.triggered.connect(self.cajaTexto.cut)
        self.action_Paste.triggered.connect(self.cajaTexto.paste)
        self.action_Find_and_Replace.triggered.connect(self.buscar_y_reemplazar)
        self.action_Acerca_de.triggered.connect(self.mostrar_acerca_de)

        self.botonAbrir.clicked.connect(self.abrir_archivo)
        self.botonComando.clicked.connect(self.analizar_codigo)
        self.cajaTexto.document().modificationChanged.connect(self.actualizar_titulo)
        self.actualizar_titulo()

    def actualizar_titulo(self, _modified: bool = False) -> None:
        nombre = self.current_file.name if self.current_file else "Sin título"
        marca = " *" if self.cajaTexto.document().isModified() else ""
        self.setWindowTitle(f"{nombre}{marca} - Editor")

    def confirmar_cambios(self) -> bool:
        if not self.cajaTexto.document().isModified():
            return True

        respuesta = QMessageBox.question(
            self,
            "Cambios sin guardar",
            "Hay cambios sin guardar. ¿Quieres guardarlos?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if respuesta == QMessageBox.StandardButton.Save:
            return self.guardar_archivo()
        return respuesta == QMessageBox.StandardButton.Discard

    def nuevo_archivo(self) -> None:
        if not self.confirmar_cambios():
            return
        self.cajaTexto.clear()
        self.salidaConsola.clear()
        self.current_file = None
        self.cajaTexto.document().setModified(False)
        self.actualizar_titulo()
        self.statusbar.showMessage("Documento nuevo", 3000)

    def abrir_archivo(self) -> None:
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo",
            str(self.current_file.parent if self.current_file else Path.home()),
            FILTRO_ARCHIVOS,
        )
        if archivo:
            self.cargar_archivo(Path(archivo))

    def cargar_archivo(self, archivo: Path) -> bool:
        try:
            contenido = archivo.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            QMessageBox.critical(self, "Error al abrir", f"No se pudo abrir el archivo:\n{error}")
            return False
        if not self.confirmar_cambios():
            return False

        self.cajaTexto.setPlainText(contenido)
        self.salidaConsola.clear()
        self.cajaTexto.document().setModified(False)
        self.current_file = archivo
        self.agregar_reciente(archivo)
        self.actualizar_titulo()
        self.statusbar.showMessage(f"Archivo abierto: {archivo}", 5000)
        return True

    def guardar_archivo(self) -> bool:
        archivo = self.current_file
        if archivo is None:
            nombre, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar archivo",
                str(Path.home() / "sin-titulo.ism"),
                FILTRO_ARCHIVOS,
            )
            if not nombre:
                return False
            archivo = Path(nombre)
            if not archivo.suffix:
                archivo = archivo.with_suffix(EXTENSION_POR_DEFECTO)

        try:
            archivo.write_text(self.cajaTexto.toPlainText(), encoding="utf-8")
        except OSError as error:
            QMessageBox.critical(self, "Error al guardar", f"No se pudo guardar el archivo:\n{error}")
            return False

        self.current_file = archivo
        self.cajaTexto.document().setModified(False)
        self.agregar_reciente(archivo)
        self.actualizar_titulo()
        self.statusbar.showMessage(f"Archivo guardado: {archivo}", 5000)
        return True

    def agregar_reciente(self, archivo: Path) -> None:
        self.recent_files = [path for path in self.recent_files if path != archivo]
        self.recent_files.insert(0, archivo)
        self.recent_files = self.recent_files[:10]
        self.actionOpen_Recent.setEnabled(True)

    def abrir_reciente(self) -> None:
        disponibles = [path for path in self.recent_files if path.is_file()]
        if not disponibles:
            self.actionOpen_Recent.setEnabled(False)
            QMessageBox.information(self, "Abrir reciente", "No hay archivos recientes disponibles.")
            return

        nombres = [str(path) for path in disponibles]
        nombre, aceptado = QInputDialog.getItem(
            self, "Abrir reciente", "Selecciona un archivo:", nombres, 0, False
        )
        if aceptado and nombre:
            self.cargar_archivo(Path(nombre))

    def buscar_y_reemplazar(self) -> None:
        buscar, aceptado = QInputDialog.getText(self, "Buscar y reemplazar", "Texto que se buscará:")
        if not aceptado or not buscar:
            return

        reemplazo, aceptado = QInputDialog.getText(
            self, "Buscar y reemplazar", f"Reemplazar «{buscar}» por:"
        )
        if not aceptado:
            return

        contenido = self.cajaTexto.toPlainText()
        cantidad = contenido.count(buscar)
        if not cantidad:
            QMessageBox.information(self, "Buscar y reemplazar", "No se encontró el texto.")
            return

        self.cajaTexto.setPlainText(contenido.replace(buscar, reemplazo))
        self.statusbar.showMessage(
            f"Se reemplazó «{buscar}» por «{reemplazo}» ({cantidad} coincidencia(s)).", 5000
        )

    def mostrar_acerca_de(self) -> None:
        QMessageBox.about(self, "Acerca de", "Editor de archivos de texto creado con PyQt6.")

    def mostrar_resultado(self, texto: str, estado: str) -> None:
        self.salidaConsola.setPlainText(texto)
        self.statusbar.showMessage(estado, 5000)

    def analizar_codigo(self) -> None:
        codigo = self.cajaTexto.toPlainText()
        if not codigo.strip():
            self.mostrar_resultado("No hay código para analizar.", "Editor vacío.")
            return

        # Fase 1: análisis léxico y sintáctico (PLY)
        lexer.lineno = 1
        try:
            instrucciones = parser.parse(codigo, lexer=lexer)
        except SyntaxError as error:
            self.mostrar_resultado(f"✖ Error sintáctico: {error}", "Error sintáctico.")
            return
        except ValueError as error:
            self.mostrar_resultado(f"✖ Error léxico: {error}", "Error léxico.")
            return
        except Exception as error:  # evita que un fallo inesperado cierre la interfaz
            self.mostrar_resultado(f"✖ Error inesperado al analizar: {error}", "Error inesperado.")
            return

        if not instrucciones:
            self.mostrar_resultado("No se encontraron instrucciones.", "Sin instrucciones.")
            return

        # Fase 2: ejecución del programa ya validado
        try:
            resultados = ejecutar(instrucciones)
        except (ErrorEjecucion, ZeroDivisionError, TypeError, ValueError) as error:
            self.mostrar_resultado(
                f"✔ Sintaxis válida.\n✖ Error de ejecución: {error}", "Error de ejecución."
            )
            return
        except Exception as error:
            self.mostrar_resultado(f"✖ Error inesperado al ejecutar: {error}", "Error inesperado.")
            return

        salida = "\n".join(resultados) if resultados else "(el programa no produjo salida)"
        self.mostrar_resultado(
            f"✔ Código válido (sin errores léxicos ni sintácticos).\n\n--- Salida ---\n{salida}",
            "Análisis completado sin errores.",
        )

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.confirmar_cambios():
            event.accept()
        else:
            event.ignore()


def main() -> int:
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
