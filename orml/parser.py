import ply.yacc as yacc
import collections

from orml.lexer import tokens

# Parsing rules

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'COMMA', 'AND', 'OR'),
    ('right', 'UMINUS'),
)

# dictionary of names
names = {}


def average(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


def p_statement_assign(t):
    'statement : NAME EQUALS expression'
    names[t[1]] = t[3]


def p_statement_expr(t):
    'statement : expression'
    t[0] = t[1]


functions = {
    'SUM': sum,
    'AVG': average
}


def p_expression_func(t):
    'expression : NAME LPAREN expression RPAREN'
    if t[1] in functions and isinstance(t[3], collections.Iterable):
        t[0] = functions[t[1]](t[3])



def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression OR expression
                  | expression AND expression
    '''
    if t[2] == '+':
        t[0] = t[1] + t[3]
    elif t[2] == '-':
        t[0] = t[1] - t[3]
    elif t[2] == '*':
        t[0] = t[1] * t[3]
    elif t[2] == '/':
        t[0] = t[1] / t[3]
    elif t[2] == '&':
        t[0] = t[1] and t[3]
    elif t[2] in '|':
        t[0] = t[1] or t[3]


def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    t[0] = -t[2]


def p_expression_group(t):
    'expression : LPAREN expression RPAREN'
    t[0] = t[2]


def p_expression_number(t):
    """
    expression : FLOAT
               | INT
    """
    t[0] = t[1]


def p_expression_array(t):
    """
    expression : array
    """
    t[0] = t[1]


def p_expression_name(t):
    'expression : NAME'
    try:
        t[0] = names[t[1]]
    except LookupError:
        print("Undefined name '%s'" % t[1])
        t[0] = 0


def p_array(t):
    'array : expression COMMA expression'
    if type(t[1]) is list:
        t[1].append(t[3])
        t[0] = t[1]
    elif type(t[3]) is list:
        t[3].insert(0, t[1])
        t[0] = t[3]
    else:
        t[0] = [t[1], t[3], ]


def p_error(t):
    print("Syntax error at '%s'" % t.value)


parser = yacc.yacc()
parse = parser.parse


if __name__ == '__main__':
    while True:
        try:
            s = input('calc > ')
        except EOFError:
            break
        print(parser.parse(s))
