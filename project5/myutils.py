#!/usr/bin/env python3

import ast
import inspect
import functools


class FunctionDispatcher:
    def __init__(self, f):
        self.f = f
        self.f_sig = inspect.signature(f)
        self.func_map = {}
       
        if not list(self.f_sig.parameters.keys())[1] == 'key':
            raise Exception('First argument of wrapped func must be key')

        self.n_posargs = 0
        self.n_kwargs = 0
        self.has_varargs = False
        self.has_kwargs = False
        for p in self.f_sig.parameters.values():
            if p.kind == p.POSITIONAL_OR_KEYWORD:
                self.n_posargs += 1
            if p.kind == p.KEYWORD_ONLY:
                self.n_kwargs += 1
            if p.kind == p.VAR_POSITIONAL:
                self.has_varargs = True
            if p.kind == p.VAR_KEYWORD:
                self.has_kwargs = True

        if not (self.has_varargs and self.has_kwargs):
            raise Exception('Wrapped function must accept *args and **kwargs')
       
        source = inspect.getsource(f)
        indent = len(source) - len(source.lstrip())
        trimmed_source = '\n'.join([s[indent:] for s in source.split('\n')])
        nodes = ast.walk(ast.parse(trimmed_source))
        if any(isinstance(n, ast.Return) for n in nodes):
            raise Exception('Wrapped function can\'t expicitly return')

    def add(self, key):
        def decorator(f):
            self.func_map[key] = f
            return f
        return decorator
    
    def __call__(self, instance, key, *args, **kwargs):
        self.f(instance, key, *args, **kwargs)
        return self.func_map[key](instance, *args, **kwargs)

    @classmethod
    def decorate(cls, f):
        # This works because dispatcher is bound by reference to the closure
        # of wrapped, so it'll have the same lifetime as the wrapped function
        # (which is understood to be a class method and thus has lifetime equal
        #  to that of the class, which is typicall the whole runtime)

        # Multiple calls to decorate will create multiple, seperate dispatchers
        # be wary
        dispatcher = cls(f)
        @functools.wraps(f)
        def wrapped(self, key, *args, **kwargs):
            return dispatcher(self, key, *args, **kwargs)
        wrapped.add = dispatcher.add
        return wrapped
