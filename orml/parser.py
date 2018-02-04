import ply.yacc as yacc
import collections

from django.db.models import Q, QuerySet
from django.db.models.base import ModelBase

from orml.helpers import App, MultiParser
from orml.lexer import tokens
from orml.utils import average

# Parsing rules

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left',  'AND', 'OR'),
    ('left', 'COMMA', 'PERIOD',),
    ('left', 'COLON',),
    ('left', 'SEMICOLON'),
    ('right', 'UMINUS'),
)

multiparser = None

def p_statement_equals(t):
    'statement : expression EQUALS expression'
    t[0] = t[1] == t[3]


def p_statement_assign(t):
    'statement : NAME ASSIGN expression'
    multiparser.set(t[1], t[3])


def p_statement_expr(t):
    'statement : expression'
    t[0] = t[1]


functions = {
    'SUM': sum,
    'AVG': average
}


def p_expression_query_filter(t):
    'expression : accessor query'
    if type(t[1]) is ModelBase:
        t[0] = t[1].objects.filter(t[2])


def p_expression_func(t):
    'expression : NAME LPAREN expression RPAREN'
    if t[1] in functions and isinstance(t[3], collections.Iterable):
        t[0] = functions[t[1]](t[3])


def p_expression_group(t):
    """expression : LPAREN expression RPAREN
    """
    t[0] = t[2]


def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
    '''
    if t[2] == '+':
        t[0] = t[1] + t[3]
    elif t[2] == '-':
        t[0] = t[1] - t[3]
    elif t[2] == '*':
        t[0] = t[1] * t[3]
    elif t[2] == '/':
        t[0] = t[1] / t[3]


def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    t[0] = -t[2]


def p_expression_vars(t):
    """
    expression : FLOAT
               | INT
               | STRING
    """
    t[0] = t[1]


def p_expression_list(t):
    """
    expression : list
               | dict
               | querychain
               | query
    """
    t[0] = t[1]


def p_expression_accessor(t):
    """
    expression : accessor
    """
    t[0] = t[1]


def p_expression_name(t):
    'expression : NAME'
    name = t[1]
    if multiparser.has(name):
        t[0] = multiparser.get(name)
    else:
        t[0] = name


def p_dict(t):
    'dict : NAME COLON expression'
    t[0] = {}
    t[0][t[1]] = t[3]


def p_dict_chain(t):
    'dict : dict COMMA dict'
    t[1].update(t[3])
    t[0] = t[1]


def p_list(t):
    'list : expression COMMA expression'
    if type(t[1]) is list:
        t[1].append(t[3])
        t[0] = t[1]
    elif type(t[3]) is list:
        t[3].insert(0, t[1])
        t[0] = t[3]
    else:
        t[0] = [t[1], t[3], ]


def p_accessor(t):
    """accessor : expression PERIOD expression
                | expression LBRACKET expression RBRACKET
    """
    name = '{}.{}'.format(t[1], t[3])
    if isinstance(t[1], App):
        t[0] = t[1].get_model(t[3])
    elif isinstance(t[1], QuerySet):
        if type(t[3]) is list:
            t[0] = t[1].values(*t[3])
        else:
            t[0] = [d.get(t[3]) for d in t[1].values(t[3])]
    elif type(t[1]) is dict:
        t[0] = t[1].get(t[3])
    else:
        t[0] = None


def p_querychain(t):
    """querychain : dict OR dict"""
    t[0] = Q(**t[1]) | Q(**t[3])


def p_querychain_or_dict(t):
    """querychain : querychain OR dict
    """
    t[0] = t[1] | Q(**t[3])


def p_querychain_or_querychain(t):
    """querychain : querychain OR querychain"""
    t[0] = t[1] | t[3]


def p_query(t):
    """query : LQBRACKET expression RQBRACKET
    """
    t[0] = t[2]


def p_query_dict(t):
    """query : LQBRACKET dict RQBRACKET
    """
    t[0] = Q(**t[2])


def p_error(t):
    print("Syntax error at '%s'" % t.value)


parser = yacc.yacc()


def parse(statements, user=None):
    global multiparser
    multiparser = MultiParser(parser, user)
    return multiparser.parse(statements)
