
# -----------------------------------------------------------------------------
# Rainman Sián
# 07-02-2020
#
# Ejemplo mi primer proyecto con Python utilizando ply en Ubuntu
# -----------------------------------------------------------------------------

tokens  = (
    'REVALUAR',
    'PARIZQ',
    'PARDER',
    'CORIZQ',
    'CORDER',
    'MAS',
    'MENOS',
    'POR',
    'DIVIDIDO',
    'DECIMAL',
    'ENTERO',
    'PTCOMA'
)

# Tokens
t_REVALUAR  = r'realiza'
t_PARIZQ    = r'\('
t_PARDER    = r'\)'
t_CORIZQ    = r'\{'
t_CORDER    = r'\}'
t_MAS       = r'suma'
t_MENOS     = r'resta'
t_POR       = r'multi'
t_DIVIDIDO  = r'divi'
t_PTCOMA    = r';'

def t_DECIMAL(t):
    r'\d+\.\d+'
    try:
        t.value = float(t.value)
    except ValueError:
        print("Floaat value too large %d", t.value)
        t.value = 0
    return t

def t_ENTERO(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t

# Caracteres ignorados
t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    columna = t.lexpos - t.lexer.lexdata.rfind("\n", 0, t.lexpos)
    raise ValueError(
        f"Carácter no válido {t.value[0]!r} en línea {t.lineno}, columna {columna}"
    )
    
# Construyendo el analizador léxico
import ply.lex as lex
lexer = lex.lex()


# Asociación de operadores y precedencia
precedence = (
    ('left','MAS','MENOS'),
    ('left','POR','DIVIDIDO'),
    ('right','UMENOS'),
    )

# Definición de la gramática
def p_instrucciones_lista(t):
    '''instrucciones    : instruccion instrucciones
                        | instruccion '''
    if len(t) == 3:
        t[0] = [t[1], *t[2]]
    else:
        t[0] = [t[1]]

def p_instrucciones_evaluar(t):
    'instruccion : REVALUAR CORIZQ expresion CORDER PTCOMA'
    t[0] = t[3]

def p_expresion_binaria(t):
    '''expresion : expresion MAS expresion
                  | expresion MENOS expresion
                  | expresion POR expresion
                  | expresion DIVIDIDO expresion'''
    if t[2] == 'suma'  : t[0] = t[1] + t[3]
    elif t[2] == 'resta': t[0] = t[1] - t[3]
    elif t[2] == 'multi': t[0] = t[1] * t[3]
    elif t[2] == 'divi': t[0] = t[1] / t[3]

def p_expresion_unaria(t):
    'expresion : MENOS expresion %prec UMENOS'
    t[0] = -t[2]

def p_expresion_agrupacion(t):
    'expresion : PARIZQ expresion PARDER'
    t[0] = t[2]

def p_expresion_number(t):
    '''expresion    : ENTERO
                    | DECIMAL'''
    t[0] = t[1]

def p_error(t):
    if t is None:
        raise SyntaxError("Fin inesperado del código")
    columna = t.lexpos - t.lexer.lexdata.rfind("\n", 0, t.lexpos)
    raise SyntaxError(
        f"Error sintáctico cerca de {t.value!r} en línea {t.lineno}, columna {columna}"
    )

import ply.yacc as yacc
parser = yacc.yacc()