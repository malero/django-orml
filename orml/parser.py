import ply.yacc as yacc
import collections

from django.db.models import Q, QuerySet, Avg, Sum, Aggregate, Count, Max, Min
from django.db.models.base import ModelBase

from orml.helpers import App, MultiParser, ArgsKwargs
from orml.lexer import tokens
from orml.utils import average, max_float, count_distinct, \
    split_queryset_arguments, count_all

# Parsing rules

precedence = (
    ('left',  'AND', 'OR'),
    ('left', 'COMMA', 'PERIOD',),
    ('left', 'COLON',),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
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
    # Aggregates
    'Sum': Sum,
    'Avg': Avg,
    'Count': Count,
    'CountAll': count_all,
    'CountDistinct': count_distinct,
    'Max': Max,
    'MaxFloat': max_float,
    'Min': Min,

    # Misc functions
    'sum': sum,
    'average': average
}


def p_expression_query_filter(t):
    'expression : accessor query'
    if type(t[1]) is ModelBase:
        t[0] = t[1].objects.filter(t[2])


def p_expression_func(t):
    """expression : NAME LPAREN expression RPAREN
                  | NAME LPAREN RPAREN
    """
    if t[1] in functions:
        if t[3] == ')':
            t[0] = functions[t[1]]()
        else:
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


def p_expression_types(t):
    """
    expression : FLOAT
               | INT
               | STRING
               | list
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
    if type(t[1]) is list and type(t[3]) is dict:
        argskwargs = ArgsKwargs()
        argskwargs.add(t[1])
        argskwargs.add(t[3])
        t[0] = argskwargs
    elif type(t[1]) is list:
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
    if isinstance(t[1], App):
        t[0] = t[1].get_model(t[3])
    elif isinstance(t[1], QuerySet):
        values, aggregate_args, aggregate_kwargs = split_queryset_arguments(t[3])
        distinct = False
        if len(values):
            if 'distinct' in values:
                values.remove('distinct')
                t[1] = t[1].values(*values).distinct()
                distinct = True
            else:
                t[1] = t[1].values(*values)

        if len(aggregate_args) or len(aggregate_kwargs):
            if distinct:
                t[1] = t[1].annotate(*aggregate_args, **aggregate_kwargs)
            else:
                t[1] = t[1].aggregate(*aggregate_args, **aggregate_kwargs)

        t[0] = t[1]
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
