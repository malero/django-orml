import ply.yacc as yacc
import collections

from django.db.models import Q, QuerySet, Avg, Sum, Aggregate, Count, Max, Min
from django.db.models.base import ModelBase
from django.forms import model_to_dict

from orml.helpers import App, MultiParser, ArgsKwargs, Scope
from orml.lexer import tokens
from orml.utils import average, max_float, count_distinct, \
    split_queryset_arguments, count_all

# Parsing rules
precedence = (
    ('left',  'AND', 'OR'),
    ('left', 'COMMA', 'PERIOD',),
    ('left', 'COLON', 'LBRACKET', 'RBRACKET'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'SEMICOLON'),
    ('right', 'UMINUS'),
)

def p_statement_equals(t):
    'statement : expression EQUALS expression'
    t[0] = t[1] == t[3]


def p_statement_assign(t):
    'statement : NAME ASSIGN expression'
    t.lexer.scope.set(t[1], t[3])


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


def p_scope(t):
    """scope : NAME PERIOD NAME
             | scope PERIOD NAME
    """
    if type(t[1]) is str:
        name = t[1]
        if t.lexer.scope.has(name):
            scope = t.lexer.scope.get(name)
            if isinstance(scope, Scope) or isinstance(scope, dict):
                t[0] = scope.get(t[3])
    else:
        t[0] = t[1].get(t[3])


def p_expression_query_filter(t):
    """expression : scope query
                  | scope dict
    """
    if type(t[1]) is ModelBase:
        if type(t[2]) is dict:
            t[0] = t[1].objects.filter(**t[2])
        else:
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
               | scope
               | argskwargs
    """
    t[0] = t[1]


def p_expression_accessor(t):
    """
    expression : accessor
    """
    t[0] = t[1]


def p_expression_name(t):
    """expression : NAME"""
    name = t[1]
    if t.lexer.scope.has(name):
        t[0] = t.lexer.scope.get(name)
    else:
        t[0] = name


def p_statement(t):
    'statement : expression SEMICOLON'
    t[0] = t[1]


def p_raw_dict(t):
    'raw_dict : NAME COLON expression'
    t[0] = {}
    t[0][t[1]] = t[3]


def p_raw_dict_chain(t):
    'raw_dict : raw_dict COMMA raw_dict'
    t[1].update(t[3])
    t[0] = t[1]


def p_argskwargs(t):
    """argskwargs : raw_list COMMA raw_dict
                  | argskwargs COMMA raw_dict
    """
    if type(t[1]) is list and type(t[3]) is dict:
        argskwargs = ArgsKwargs()
        argskwargs.add(t[1])
    else:
        argskwargs = t[1]
    argskwargs.add(t[3])
    t[0] = argskwargs


def p_raw_list(t):
    """raw_list : expression COMMA expression
                | raw_list COMMA expression
                | raw_list COMMA raw_list
    """
    if type(t[1]) is list:
        t[1].append(t[3])
        t[0] = t[1]
    elif type(t[3]) is list:
        t[3].insert(0, t[1])
        t[0] = t[3]
    else:
        t[0] = [t[1], t[3], ]


def p_list(t):
    """list : LBRACKET raw_list RBRACKET"""
    t[0] = t[2]


def p_list_piped(t):
    """list : expression PIPE list
            | expression PIPE NAME
            | expression PIPE INT
    """
    if type(t[3]) is list:
        t[0] = [[l[n] for n in t[3]] for l in t[1]]
    elif type(t[3]) is str:
        t[0] = [l.get(t[3]) for l in t[1]]
    elif type(t[3]) is int:
        t[0] = [l[t[3]] for l in t[1]]


def p_accessor(t):
    """accessor : expression LBRACKET expression RBRACKET
                | expression LBRACKET raw_list RBRACKET
    """
    if type(t[1]) is list and type(t[3]) is int:
        t[0] = t[1][t[3]]
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

        # Convert models to dicts
        # if t[1] is still a queryset, convert all models to dicts
        if isinstance(t[1], QuerySet) and isinstance(t[1][0], ModelBase):
            t[0] = [model_to_dict(m) for m in t[1]]
        else:
            t[0] = t[1]
    elif type(t[1]) is dict:
        t[0] = t[1].get(t[3])
    else:
        t[0] = None


def p_querychain(t):
    """querychain : raw_dict OR raw_dict
                  | raw_dict OR dict
                  | dict OR raw_dict
                  | dict OR dict
    """
    t[0] = Q(**t[1]) | Q(**t[3])


def p_querychain_or_dict(t):
    """querychain : querychain OR raw_dict
                  | querychain OR dict
    """
    t[0] = t[1] | Q(**t[3])


def p_querychain_or_querychain(t):
    """querychain : querychain OR querychain"""
    t[0] = t[1] | t[3]


def p_query(t):
    """query : LQBRACKET querychain RQBRACKET
        """
    t[0] = t[2]


def p_query_dict(t):
    """dict : LQBRACKET raw_dict RQBRACKET
    """
    t[0] = t[2]


def p_error(t):
    print("Syntax error at '%s'" % t.value)


parser = yacc.yacc()


def parse(statements, user=None):
    multiparser = MultiParser(parser, user)
    return multiparser.parse(statements)
