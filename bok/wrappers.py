#!/usr/bin/env python3

from collections import Iterable

from . import array_module


class EmptyNode:
    pass


def filter_word_defs(ops):
    return [
        op for op in ops
        if op is not EmptyNode
    ]


class ReprWrapper:
    repr_fmt = '<{0}>'

    def __repr__(self):
        return self.repr_fmt.format(self.__name__)


class PyWr(ReprWrapper):
    repr_fmt = '<py:{0}>'

    def __init__(self, obj):
        self.obj = obj
        self.__name__ = obj.__name__
        self.__doc__ = obj.__doc__

    def __call__(self, stack):
        if stack.args_loaded:
            stack.push(self.obj(*stack.args, **stack.kwargs))
        else:
            top = stack[-1]
            if isinstance(top, array_module.ndarray):
                stack[-1] = self.obj(top)
            elif not isinstance(top, Iterable):
                stack[-1] = self.obj(top)
            else:
                stack[-1] = self.obj(*top)
        stack.clear_args()


class ArrayWr(PyWr):
    repr_fmt = '<@{0}>'


class CallWr(ReprWrapper):
    def __init__(self, name, words):
        self.name = name
        self.__name__ = name
        self.words = words

    def __call__(self, stack):
        return self.words[self.name](stack)

    @property
    def __doc__(self):
        return self.words[self.name].__doc__


class VarWr(ReprWrapper):
    repr_fmt = '<:{0}>'

    def __init__(self, name):
        self.__name__ = name
        self.val = None

    def new(self, stack):
        self.val = stack.pop()

    def clear(self):
        self.val = None

    def __call__(self, stack):
        stack.push(self.val)


class WordWr(ReprWrapper):
    def __init__(self, name, ops, doc):
        self.__doc__ = doc
        self.__name__ = name
        self.ops = filter_word_defs(ops)
        self.vars = self._get_vars()

    def _get_vars(self):
        """
        The method `.new` of an instance of VarWrapper is actually the op
        that's in the list, but we want the instance itself.
        """
        return set(
            op.__self__ for op in self.ops
            if hasattr(op, '__self__') and isinstance(op.__self__, VarWrapper)
        )

    def _clear_vars(self):
        for var in self.vars:
            var.clear()

    def __call__(self, stack):
        try:
            for op in self.ops:
                if callable(op):
                    op(stack)
                else:
                    stack.append(op)
        except WordReturn:
            pass
        if self.vars:
            self._clear_vars()


