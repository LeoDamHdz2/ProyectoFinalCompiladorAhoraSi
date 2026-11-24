import unittest

from gramatica import ejecutar, lexer, parser


class PruebasGramatica(unittest.TestCase):
    def ejecutar_codigo(self, codigo: str) -> list[str]:
        lexer.lineno = 1
        instrucciones = parser.parse(codigo, lexer=lexer)
        return ejecutar(instrucciones)

    def test_variables_tipadas_y_print(self) -> None:
        salida = self.ejecutar_codigo(
            'intevil cantidad = 2; floatnite precio = 1.5; '
            'stringfighter etiqueta = "total"; '
            'printal(etiqueta, cantidad * precio);'
        )
        self.assertEqual(salida, ["total 3.0"])

    def test_bucles_y_seleccion(self) -> None:
        salida = self.ejecutar_codigo(
            'intevil i = 0; whilecraft (i < 2) { '
            'ifcraft (i == 0) { printal("inicio"); } '
            'elselda { printal("fin"); } '
            'i = i + 1; } '
            'fornite (intevil j = 0; j < 2; j = j + 1) { printal(j); }'
        )
        self.assertEqual(salida, ["inicio", "fin", "0", "1"])

    def test_palabras_reservadas_de_videojuegos(self) -> None:
        salida = self.ejecutar_codigo(
            'ifcraft (truetroid orizon fallse) { printal("logico"); } '
            'ifcraft (truetroid andcraft truetroid) { printal("conjuncion"); } '
            'ifcraft (notality fallse) { printal("negacion"); } '
            'realizelda{1suma1};'
        )
        self.assertEqual(
            salida, ["logico", "conjuncion", "negacion", "Resultado 1: 2"]
        )

    def test_sintaxis_realizelda(self) -> None:
        salida = self.ejecutar_codigo(
            "realizelda{1suma1}; realizelda{1multiresta2};"
        )
        self.assertEqual(salida, ["Resultado 1: 2", "Resultado 2: -2"])

    def test_asignacion_respeta_tipo(self) -> None:
        with self.assertRaisesRegex(ValueError, "requiere un valor de tipo int"):
            self.ejecutar_codigo('intevil cantidad = 1; cantidad = "texto";')


if __name__ == "__main__":
    unittest.main()
