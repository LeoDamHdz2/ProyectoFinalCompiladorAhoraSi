import unittest

from gramatica import ejecutar, lexer, parser


class PruebasGramatica(unittest.TestCase):
    def ejecutar_codigo(self, codigo: str) -> list[str]:
        lexer.lineno = 1
        instrucciones = parser.parse(codigo, lexer=lexer)
        return ejecutar(instrucciones)

    def test_variables_tipadas_y_print(self) -> None:
        salida = self.ejecutar_codigo(
            'int cantidad = 2; float precio = 1.5; '
            'string etiqueta = "total"; print(etiqueta, cantidad * precio);'
        )
        self.assertEqual(salida, ["total 3.0"])

    def test_bucles_y_seleccion(self) -> None:
        salida = self.ejecutar_codigo(
            'int i = 0; while (i < 2) { '
            'if (i == 0) { print("inicio"); } else { print("fin"); } '
            'i = i + 1; } '
            'for (int j = 0; j < 2; j = j + 1) { print(j); }'
        )
        self.assertEqual(salida, ["inicio", "fin", "0", "1"])

    def test_sintaxis_legacy_realiza(self) -> None:
        salida = self.ejecutar_codigo(
            "realiza{1suma1}; realiza{1multiresta2};"
        )
        self.assertEqual(salida, ["Resultado 1: 2", "Resultado 2: -2"])

    def test_asignacion_respeta_tipo(self) -> None:
        with self.assertRaisesRegex(ValueError, "requiere un valor de tipo int"):
            self.ejecutar_codigo('int cantidad = 1; cantidad = "texto";')


if __name__ == "__main__":
    unittest.main()
