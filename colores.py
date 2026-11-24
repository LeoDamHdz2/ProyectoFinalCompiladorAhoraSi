
import re
import keyword

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import (
    QColor,
    QFont,
    QSyntaxHighlighter,
    QTextCharFormat
)


class Resaltador(QSyntaxHighlighter):
    def __init__(self, documento):
        super().__init__(documento)
        self.reglas = []

        def formato(color, negrita=False):
            estilo = QTextCharFormat()
            estilo.setForeground(QColor(color))
            if negrita:
                estilo.setFontWeight(QFont.Weight.Bold)
            return estilo

        # Palabras reservadas de Python
        reservadas = keyword.kwlist + [
            "intevil", "floatnite", "stringfighter", "printal",
            "ifcraft", "elselda", "whilecraft", "fornite",
            "truetroid", "fallse", "andcraft", "orizon", "notality",
            "realizelda",
            "entero", "decimal", "texto",
            "cadena", "booleano",
            "mostrar", "imprimir",
            "inicio", "fin", "mision",
            "verdadero", "falso"
        ]

        for palabra in reservadas:
            patron = r"\b" + re.escape(palabra) + r"\b"
            self.reglas.append((
                QRegularExpression(patron),
                formato("#C586C0", True)
            ))

        # Funciones conocidas
        funciones = [
            "printal", "input", "len",
            "range", "int", "float", "str"
        ]

        for palabra in funciones:
            patron = r"\b" + re.escape(palabra) + r"\b"
            self.reglas.append((
                QRegularExpression(patron),
                formato("#DCDCAA")
            ))

        # Números
        self.reglas.append((
            QRegularExpression(r"\b\d+(\.\d+)?\b"),
            formato("#B5CEA8")
        ))

        # Operadores
        self.reglas.append((
            QRegularExpression(r"[+\-*/=<>!]+"),
            formato("#D4D4D4")
        ))

        # Cadenas entre comillas
        self.reglas.append((
            QRegularExpression(r'"(?:\\.|[^"\\])*"'),
            formato("#CE9178")
        ))

        self.reglas.append((
            QRegularExpression(r"'(?:\\.|[^'\\])*'"),
            formato("#CE9178")
        ))

        # Comentarios
        self.reglas.append((
            QRegularExpression(r"#[^\n]*"),
            formato("#6A9955")
        ))

    def highlightBlock(self, texto):
        for patron, estilo in self.reglas:
            coincidencias = patron.globalMatch(texto)

            while coincidencias.hasNext():
                coincidencia = coincidencias.next()
                inicio = coincidencia.capturedStart()
                longitud = coincidencia.capturedLength()

                self.setFormat(inicio, longitud, estilo)
