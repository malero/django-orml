tokens = (
    'PIPE', 'NAME', 'COLON', 'SEMICOLON', 'COMMA', 'PERIOD', 'OR', 'AND',
    'FLOAT', 'INT', 'STRING',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'EQUALS', 'ASSIGN',
    'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'LQBRACKET', 'RQBRACKET',
)

# Tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_EQUALS = r'=='
t_ASSIGN = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LQBRACKET = r'\{'
t_RQBRACKET = r'\}'
t_COLON = r':'
t_SEMICOLON = r';'
t_COMMA = r','
t_PERIOD = r'\.'
t_PIPE = r'\@'
t_OR = r'\|'
t_AND = r'&{2}'
t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'


def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t


def t_INT(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t


def t_STRING(t):
    r'\"[^\"]+\"'
    t.value = str(t.value[1:-1])
    return t


# Ignored characters
t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
