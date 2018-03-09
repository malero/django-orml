import ply.lex as lex

from django.contrib.contenttypes.models import ContentType

from orml import lexer


class Scope:
    def __init__(self):
        self.data = {}

    def has(self, name):
        if name in self.data:
            return True
        return False

    def get(self, name):
        if name in self.data:
            return self.data[name]

    def set(self, name, var):
        self.data[name] = var


class App(Scope):
    def __init__(self, label):
        super(App, self).__init__()
        self.label = label
        self.models = []
        self.model_names = []

    def add_model(self, model):
        self.model_names.append(model.model)
        self.models.append(model)
        self.set(model.model, model.model_class())

    def is_model(self, name):
        return name in self.model_names

    def get_model(self, name):
        for t in self.models:
            if name == t.model:
                return t.model_class()


class MultiParser:
    def __init__(self, parser, user):
        # User for permissions
        self.user = user

        # Scopes
        self.protected = {}
        self.public = {}

        # apps
        self.content_types = ContentType.objects.all()
        for t in self.content_types:
            if not self.app_exists(t.app_label):
                app = self.add_app(t.app_label)
            else:
                app = self.get_app(t.app_label)
            app.add_model(t)

        # Execution stack and result
        self.stack = []
        self.result = None

        # Yacc Parser
        self.parser = parser

        # Lexer
        self.lexer = lex.lex(module=lexer)
        self.lexer.scope = self

    def app_exists(self, label):
        if label in self.protected and isinstance(self.protected[label], App):
            return True
        return False

    def get_app(self, label):
        if self.app_exists(label):
            return self.protected[label]

    def add_app(self, label):
        app = App(label)
        self.protected[label] = app
        return app

    def parse(self, statements):
        if type(statements) is str:
            statements = statements.split('\n')
        for s in statements:
            if not s: continue
            self.stack.append(self.parser.parse(s, lexer=self.lexer))

        # Assign last stack statement result as multi parser result
        self.result = self.stack[-1]

        return self.result

    def has(self, name):
        if name in self.protected:
            return True

        if name in self.public:
            return True

        return False

    def get(self, name):
        if name in self.protected:
            return self.protected[name]

        if name in self.public:
            return self.public[name]

    def set(self, name, var):
        self.public[name] = var


class ArgsKwargs:
    def __init__(self):
        self.args = []
        self.kwargs = {}

    def add(self, a):
        if type(a) is list:
            self.args += a
        elif type(a) is dict:
            self.kwargs.update(a)
        elif isinstance(a, ArgsKwargs):
            self.args += a.args
            self.kwargs.update(a.kwargs)

    def get(self, name):
        return self.kwargs.get(name)
