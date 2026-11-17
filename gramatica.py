import ast
from dataclasses import dataclass
from typing import TypeAlias

tokens = (
    "REVALUAR",
    "PARIZQ",
    "PARDER",
    "CORIZQ",
    "CORDER",
    "MAS",
    "MENOS",
    "POR",
    "DIVIDIDO",
    "DECIMAL",
    "ENTERO",
    "PTCOMA",
    "COMA",
    "ID",
    "STRING",
    "INT",
    "FLOAT",
    "STRING_TYPE",
    "PRINT",
    "IF",
    "ELSE",
    "WHILE",
    "FOR",
    "TRUE",
    "FALSE",
    "ASIGN",
    "IGUAL",
    "DISTINTO",
    "MENOR",
    "MENORIGUAL",
    "MAYOR",
    "MAYORIGUAL",
    "AND",
    "OR",
    "NOT",
)

reserved = {
    "int": "INT",
    "float": "FLOAT",
    "string": "STRING_TYPE",
    "print": "PRINT",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "for": "FOR",
    "true": "TRUE",
    "false": "FALSE",
    "and": "AND",
    "or": "OR",
    "not": "NOT",
}

t_PARIZQ = r"\("
t_PARDER = r"\)"
t_CORIZQ = r"\{"
t_CORDER = r"\}"
t_PTCOMA = r";"
t_COMA = r","
t_ASIGN = r"="
t_IGUAL = r"=="
t_DISTINTO = r"!="
t_MENORIGUAL = r"<="
t_MAYORIGUAL = r">="
t_MENOR = r"<"
t_MAYOR = r">"
t_AND = r"&&"
t_OR = r"\|\|"
t_NOT = r"!"


def t_STRING(t):
    r"""("([^"\\]|\\.)*"|'([^'\\]|\\.)*')"""
    try:
        t.value = ast.literal_eval(t.value)
    except (SyntaxError, ValueError) as error:
        raise ValueError(f"Texto no válido en línea {t.lineno}") from error
    return t


def t_DECIMAL(t):
    r"\d+\.\d+"
    t.value = float(t.value)
    return t


def t_ENTERO(t):
    r"\d+"
    t.value = int(t.value)
    return t


def t_REVALUAR(t):
    r"realiza\b"
    return t


def t_MAS(t):
    r"suma(?=\d|suma|resta|multi|divi|\b)|\+"
    return t


def t_MENOS(t):
    r"resta(?=\d|suma|resta|multi|divi|\b)|-"
    return t


def t_POR(t):
    r"multi(?=\d|suma|resta|multi|divi|\b)|\*"
    return t


def t_DIVIDIDO(t):
    r"divi(?=\d|suma|resta|multi|divi|\b)|/"
    return t


def t_ID(t):
    r"[A-Za-z_][A-Za-z0-9_]*"
    t.type = reserved.get(t.value, "ID")
    return t


t_ignore = " \t\r"


def t_newline(t):
    r"\n+"
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    columna = t.lexpos - t.lexer.lexdata.rfind("\n", 0, t.lexpos)
    raise ValueError(
        f"Carácter no válido {t.value[0]!r} en línea {t.lineno}, columna {columna}"
    )


import ply.lex as lex

lexer = lex.lex()

precedence = (
    ("nonassoc", "IFX"),
    ("nonassoc", "ELSE"),
    ("left", "OR"),
    ("left", "AND"),
    ("left", "IGUAL", "DISTINTO"),
    ("nonassoc", "MENOR", "MENORIGUAL", "MAYOR", "MAYORIGUAL"),
    ("left", "MAS", "MENOS"),
    ("left", "POR", "DIVIDIDO"),
    ("right", "NOT", "UMENOS"),
)


@dataclass(frozen=True)
class Literal:
    value: int | float | str | bool


@dataclass(frozen=True)
class Variable:
    name: str


@dataclass(frozen=True)
class Binary:
    operator: str
    left: "Expression"
    right: "Expression"


@dataclass(frozen=True)
class Unary:
    operator: str
    operand: "Expression"


Expression: TypeAlias = Literal | Variable | Binary | Unary


@dataclass(frozen=True)
class Declaration:
    type_name: str
    name: str
    initializer: Expression | None


@dataclass(frozen=True)
class Assignment:
    name: str
    expression: Expression


@dataclass(frozen=True)
class ExpressionStatement:
    expression: Expression


@dataclass(frozen=True)
class PrintStatement:
    expressions: list[Expression]


@dataclass(frozen=True)
class Block:
    statements: list["Statement"]


@dataclass(frozen=True)
class IfStatement:
    condition: Expression
    consequent: Block
    alternative: Block | None


@dataclass(frozen=True)
class WhileStatement:
    condition: Expression
    body: Block


@dataclass(frozen=True)
class ForStatement:
    initializer: Declaration | Assignment | None
    condition: Expression | None
    update: Assignment | None
    body: Block


Statement: TypeAlias = (
    Declaration
    | Assignment
    | ExpressionStatement
    | PrintStatement
    | Block
    | IfStatement
    | WhileStatement
    | ForStatement
)


def p_programa(t):
    "programa : instrucciones_opcionales"
    t[0] = t[1]


def p_instrucciones_opcionales(t):
    """instrucciones_opcionales : instrucciones
                                | empty"""
    t[0] = t[1] if t[1] is not None else []


def p_instrucciones_lista(t):
    """instrucciones : instruccion instrucciones
                     | instruccion"""
    t[0] = [t[1], *t[2]] if len(t) == 3 else [t[1]]


def p_instruccion(t):
    """instruccion : declaracion
                   | asignacion PTCOMA
                   | instruccion_print
                   | bloque
                   | instruccion_if
                   | instruccion_while
                   | instruccion_for
                   | REVALUAR CORIZQ expresion CORDER PTCOMA"""
    if len(t) == 6:
        t[0] = ExpressionStatement(t[3])
    elif len(t) == 3:
        t[0] = t[1]
    else:
        t[0] = t[1]


def p_declaracion(t):
    """declaracion : tipo ID PTCOMA
                   | tipo ID ASIGN expresion PTCOMA"""
    initializer = t[4] if len(t) == 6 else None
    t[0] = Declaration(t[1], t[2], initializer)


def p_tipo(t):
    """tipo : INT
            | FLOAT
            | STRING_TYPE"""
    t[0] = {"INT": "int", "FLOAT": "float", "STRING_TYPE": "string"}[t.slice[1].type]


def p_asignacion(t):
    "asignacion : ID ASIGN expresion"
    t[0] = Assignment(t[1], t[3])


def p_instruccion_print(t):
    "instruccion_print : PRINT PARIZQ argumentos_opcionales PARDER PTCOMA"
    t[0] = PrintStatement(t[3])


def p_argumentos_opcionales(t):
    """argumentos_opcionales : argumentos
                             | empty"""
    t[0] = t[1] if t[1] is not None else []


def p_argumentos(t):
    """argumentos : expresion
                  | argumentos COMA expresion"""
    t[0] = [*t[1], t[3]] if len(t) == 4 else [t[1]]


def p_bloque(t):
    "bloque : CORIZQ instrucciones_opcionales CORDER"
    t[0] = Block(t[2])


def p_instruccion_if(t):
    """instruccion_if : IF PARIZQ expresion PARDER bloque %prec IFX
                      | IF PARIZQ expresion PARDER bloque ELSE bloque"""
    t[0] = IfStatement(t[3], t[5], t[7] if len(t) == 8 else None)


def p_instruccion_while(t):
    "instruccion_while : WHILE PARIZQ expresion PARDER bloque"
    t[0] = WhileStatement(t[3], t[5])


def p_instruccion_for(t):
    "instruccion_for : FOR PARIZQ for_inicializador PTCOMA expresion_opcional PTCOMA asignacion_opcional PARDER bloque"
    t[0] = ForStatement(t[3], t[5], t[7], t[9])


def p_for_inicializador(t):
    """for_inicializador : declaracion_for
                         | asignacion
                         | empty"""
    t[0] = t[1]


def p_declaracion_for(t):
    """declaracion_for : tipo ID
                       | tipo ID ASIGN expresion"""
    initializer = t[4] if len(t) == 5 else None
    t[0] = Declaration(t[1], t[2], initializer)


def p_expresion_opcional(t):
    """expresion_opcional : expresion
                          | empty"""
    t[0] = t[1]


def p_asignacion_opcional(t):
    """asignacion_opcional : asignacion
                           | empty"""
    t[0] = t[1]


def p_expresion_binaria(t):
    """expresion : expresion MAS expresion
                 | expresion MENOS expresion
                 | expresion POR expresion
                 | expresion DIVIDIDO expresion
                 | expresion IGUAL expresion
                 | expresion DISTINTO expresion
                 | expresion MENOR expresion
                 | expresion MENORIGUAL expresion
                 | expresion MAYOR expresion
                 | expresion MAYORIGUAL expresion
                 | expresion AND expresion
                 | expresion OR expresion"""
    t[0] = Binary(t.slice[2].type, t[1], t[3])


def p_expresion_unaria(t):
    """expresion : MENOS expresion %prec UMENOS
                 | NOT expresion"""
    t[0] = Unary(t.slice[1].type, t[2])


def p_expresion_agrupacion(t):
    "expresion : PARIZQ expresion PARDER"
    t[0] = t[2]


def p_expresion_valor(t):
    """expresion : ENTERO
                 | DECIMAL
                 | STRING
                 | TRUE
                 | FALSE"""
    value = t[1]
    if t.slice[1].type == "TRUE":
        value = True
    elif t.slice[1].type == "FALSE":
        value = False
    t[0] = Literal(value)


def p_expresion_variable(t):
    "expresion : ID"
    t[0] = Variable(t[1])


def p_empty(t):
    "empty :"
    t[0] = None


def p_error(t):
    if t is None:
        raise SyntaxError("Fin inesperado del código")
    columna = t.lexpos - t.lexer.lexdata.rfind("\n", 0, t.lexpos)
    raise SyntaxError(
        f"Error sintáctico cerca de {t.value!r} en línea {t.lineno}, columna {columna}"
    )


class ErrorEjecucion(ValueError):
    pass


class _Entorno:
    def __init__(self) -> None:
        self.ambitos: list[dict[str, tuple[str, int | float | str]]] = [{}]

    def buscar(self, nombre: str) -> tuple[str, int | float | str]:
        for ambito in reversed(self.ambitos):
            if nombre in ambito:
                return ambito[nombre]
        raise ErrorEjecucion(f"La variable '{nombre}' no está declarada.")

    def obtener(self, nombre: str) -> int | float | str:
        return self.buscar(nombre)[1]

    def declarar(self, tipo: str, nombre: str, valor: object) -> None:
        ambito = self.ambitos[-1]
        if nombre in ambito:
            raise ErrorEjecucion(f"La variable '{nombre}' ya está declarada.")
        ambito[nombre] = (tipo, _convertir_tipo(tipo, nombre, valor))

    def asignar(self, nombre: str, valor: object) -> None:
        for ambito in reversed(self.ambitos):
            if nombre in ambito:
                tipo, _ = ambito[nombre]
                ambito[nombre] = (tipo, _convertir_tipo(tipo, nombre, valor))
                return
        raise ErrorEjecucion(f"La variable '{nombre}' no está declarada.")


def _convertir_tipo(tipo: str, nombre: str, valor: object) -> int | float | str:
    if tipo == "int" and type(valor) is int:
        return valor
    if tipo == "float" and type(valor) in (int, float):
        return float(valor)
    if tipo == "string" and isinstance(valor, str):
        return valor
    raise ErrorEjecucion(f"La variable '{nombre}' requiere un valor de tipo {tipo}.")


def _evaluar(expresion: Expression, entorno: _Entorno) -> int | float | str | bool:
    if isinstance(expresion, Literal):
        return expresion.value
    if isinstance(expresion, Variable):
        return entorno.obtener(expresion.name)
    if isinstance(expresion, Unary):
        valor = _evaluar(expresion.operand, entorno)
        if expresion.operator == "MENOS":
            return -valor
        return not valor

    izquierda = _evaluar(expresion.left, entorno)
    if expresion.operator == "AND":
        return bool(izquierda) and bool(_evaluar(expresion.right, entorno))
    if expresion.operator == "OR":
        return bool(izquierda) or bool(_evaluar(expresion.right, entorno))

    derecha = _evaluar(expresion.right, entorno)
    operaciones = {
        "MAS": lambda: izquierda + derecha,
        "MENOS": lambda: izquierda - derecha,
        "POR": lambda: izquierda * derecha,
        "DIVIDIDO": lambda: izquierda / derecha,
        "IGUAL": lambda: izquierda == derecha,
        "DISTINTO": lambda: izquierda != derecha,
        "MENOR": lambda: izquierda < derecha,
        "MENORIGUAL": lambda: izquierda <= derecha,
        "MAYOR": lambda: izquierda > derecha,
        "MAYORIGUAL": lambda: izquierda >= derecha,
    }
    return operaciones[expresion.operator]()


MAX_ITERACIONES = 100_000


def _ejecutar_instruccion(
    instruccion: Statement,
    entorno: _Entorno,
    salida: list[str],
    contador_resultados: list[int],
    iteraciones_totales: list[int],
) -> None:
    if isinstance(instruccion, Declaration):
        valor = (
            _evaluar(instruccion.initializer, entorno)
            if instruccion.initializer is not None
            else {"int": 0, "float": 0.0, "string": ""}[instruccion.type_name]
        )
        entorno.declarar(instruccion.type_name, instruccion.name, valor)
    elif isinstance(instruccion, Assignment):
        entorno.asignar(instruccion.name, _evaluar(instruccion.expression, entorno))
    elif isinstance(instruccion, ExpressionStatement):
        resultado = _evaluar(instruccion.expression, entorno)
        contador_resultados[0] += 1
        salida.append(f"Resultado {contador_resultados[0]}: {resultado}")
    elif isinstance(instruccion, PrintStatement):
        valores = (_evaluar(expresion, entorno) for expresion in instruccion.expressions)
        salida.append(" ".join(str(valor) for valor in valores))
    elif isinstance(instruccion, Block):
        entorno.ambitos.append({})
        try:
            for sentencia in instruccion.statements:
                _ejecutar_instruccion(
                    sentencia, entorno, salida, contador_resultados, iteraciones_totales
                )
        finally:
            entorno.ambitos.pop()
    elif isinstance(instruccion, IfStatement):
        rama = (
            instruccion.consequent
            if _evaluar(instruccion.condition, entorno)
            else instruccion.alternative
        )
        if rama is not None:
            _ejecutar_instruccion(
                rama, entorno, salida, contador_resultados, iteraciones_totales
            )
    elif isinstance(instruccion, WhileStatement):
        while _evaluar(instruccion.condition, entorno):
            if iteraciones_totales[0] >= MAX_ITERACIONES:
                raise ErrorEjecucion("El bucle superó el límite de iteraciones.")
            iteraciones_totales[0] += 1
            _ejecutar_instruccion(
                instruccion.body, entorno, salida, contador_resultados, iteraciones_totales
            )
    elif isinstance(instruccion, ForStatement):
        entorno.ambitos.append({})
        try:
            if instruccion.initializer is not None:
                _ejecutar_instruccion(
                    instruccion.initializer,
                    entorno,
                    salida,
                    contador_resultados,
                    iteraciones_totales,
                )
            while instruccion.condition is None or _evaluar(instruccion.condition, entorno):
                if iteraciones_totales[0] >= MAX_ITERACIONES:
                    raise ErrorEjecucion("El bucle superó el límite de iteraciones.")
                iteraciones_totales[0] += 1
                _ejecutar_instruccion(
                    instruccion.body, entorno, salida, contador_resultados, iteraciones_totales
                )
                if instruccion.update is not None:
                    _ejecutar_instruccion(
                        instruccion.update,
                        entorno,
                        salida,
                        contador_resultados,
                        iteraciones_totales,
                    )
        finally:
            entorno.ambitos.pop()


def ejecutar(programa: list[Statement]) -> list[str]:
    entorno = _Entorno()
    salida: list[str] = []
    contador_resultados = [0]
    iteraciones_totales = [0]
    for instruccion in programa:
        _ejecutar_instruccion(
            instruccion, entorno, salida, contador_resultados, iteraciones_totales
        )
    return salida


import ply.yacc as yacc

parser = yacc.yacc(write_tables=False, debug=False)
