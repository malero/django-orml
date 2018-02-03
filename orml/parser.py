import ply.yacc as yacc
import collections

from django.contrib.contenttypes.models import ContentType

from orml.lexer import tokens

# Parsing rules

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'COMMA', 'PERIOD', 'AND', 'OR'),
    ('left', 'COLON'),
    ('right', 'UMINUS'),
)

# dictionary of names
names = {}


model_names = []
content_types = []


def setup():
    global model_names
    global content_types
    content_types = ContentType.objects.all()
    model_names = ['{}.{}'.format(t.app_label, t.model) for t in content_types]


def is_model(name):
    if not len(content_types):
        setup()
    return name in model_names


def get_model(name):
    if not len(content_types):
        setup()

    app_label, model_name = name.split('.')
    for t in content_types:
        if app_label == t.app_label and model_name == t.model:
            return t.model_class()


def average(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


def p_statement_equals(t):
    'statement : expression EQUALS expression'
    t[0] = t[1] == t[3]


def p_statement_assign(t):
    'statement : NAME ASSIGN expression'
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


def p_expression_list(t):
    """
    expression : list
               | dict
    """
    t[0] = t[1]


def p_expression_accessor(t):
    """
    expression : accessor
    """
    t[0] = t[1]


def p_expression_name(t):
    'expression : NAME'
    v = t[1]
    if v in names:
        t[0] = names[v]
    else:
        t[0] = v


def p_dict(t):
    'dict : expression COLON expression'
    t[0] = {}
    t[0][t[1]] = t[3]


def p_list(t):
    'list : expression COMMA expression'
    if type(t[1]) is list:
        t[1].append(t[3])
        t[0] = t[1]
    elif type(t[3]) is list:
        t[3].insert(0, t[1])
        t[0] = t[3]
    elif type(t[1]) is dict and type(t[3]) is dict:
        t[1].update(t[3])
        t[0] = t[1]
    else:
        t[0] = [t[1], t[3], ]


def p_accessor(t):
    """accessor : expression PERIOD expression
                | expression LBRACKET expression RBRACKET
    """
    name = '{}.{}'.format(t[1], t[3])
    if hasattr(t[1], t[3]):
        t[0] = getattr(t[1], t[3])
    elif is_model(name):
        t[0] = get_model(name)
    else:
        t[0] = None


def p_query(t):
    """query : LQBRACKET expression RQBRACKET
    """


def p_error(t):
    print("Syntax error at '%s'" % t.value)


parser = yacc.yacc()


def parse(q):
    global names
    names = {}
    return parser.parse(q)


if __name__ == '__main__':
    while True:
        try:
            s = input('calc > ')
        except EOFError:
            break
        print(parser.parse(s))
