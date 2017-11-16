import os
import copy
import warnings
from collections import Iterable

from lark import Lark, Transformer, Tree
from lark.lexer import Token

from .stack import BUILTINS, Stack, WordReturn


warnings.simplefilter('default')
try:
    import numpy as array_module
except ImportError:
    array_module = None
    msg = 'Module "numpy" not found, array "@" literals will not be supported'
    warnings.warn(msg, ImportWarning)


LIB_PATH = '/home/brian/code/bok/lib'


def read_grammar():
    filen = os.path.join(os.path.dirname(__file__), 'grammar.g')
    with open(filen, 'r') as f:
        return Lark(f, start='start', parser='lalr', lexer='contextual')


def scope_words(tree, scope=None, words=None):
    if scope is None:
        scope = []
    if words is None:
        words = []
    for subtree in tree.children:
        if not isinstance(subtree, Tree):
            continue
        if subtree.data == 'list':
            scope_words(subtree, scope, words)
        elif subtree.data == 'var':
            name = subtree.children[0].value
            scoped_name = '.'.join([*scope, name]) if scope else name
            words.append(scoped_name)
            subtree.children[0].value = scoped_name
        elif subtree.data in ('call', 'dot'):
            name = subtree.children[0].value
            test_scope = scope.copy()
            while test_scope:
                scoped_name = '.'.join([*test_scope, name])
                if scoped_name in words:
                    subtree.children[0].value = scoped_name
                    break
                test_scope.pop()
        elif subtree.data == 'word':
            name = subtree.children[0].value
            scoped_name = '.'.join([*scope, name]) if scope else name
            scope.append(name)
            words.append(scoped_name)
            subtree.children[0].value = scoped_name
            scope_words(subtree, scope, words=words)
            scope.pop()


class ReprWrapper:
    repr_fmt = '<{0}>'

    def __repr__(self):
        return self.repr_fmt.format(self.__name__)


class ArrayWrapper(ReprWrapper):
    repr_fmt = '<@{0}>'

    def __init__(self, obj):
        self.obj = obj
        self.__name__ = obj.__name__
        self.__doc__ = obj.__doc__

    def __call__(self, stack):
        top = stack[-1]
        if isinstance(top, array_module.ndarray):
            stack[-1] = self.obj(top)
        elif not isinstance(top, Iterable):
            stack[-1] = self.obj(top)
        else:
            stack[-1] = self.obj(*top)


class CallWrapper(ReprWrapper):
    def __init__(self, name, words):
        self.name = name
        self.__name__ = name
        self.words = words

    def __call__(self, stack):
        return self.words[self.name](stack)

    @property
    def __doc__(self):
        return self.words[self.name].__doc__


class VarWrapper:
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


class EmptyNode:
    pass


def filter_word_defs(ops):
    return [
        op for op in ops
        if op is not EmptyNode
    ]


class WordWrapper(ReprWrapper):
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


class ReduceTree(Transformer):
    def __init__(self, words, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.words = words

    def number(self, tree):
        return eval(tree[0])

    def string(self, tree):
        return eval(tree[0])

    def operator(self, tree):
        return self.words[tree[0]]

    def true_(self, tree):
        return True

    def false_(self, tree):
        return False

    def none_(self, tree):
        return None

    def list(self, tree):
        return list(tree)

    def array(self, tree):
        obj = array_module
        for child in tree:
            obj = getattr(obj, child)
        return ArrayWrapper(obj)

    def dot(self, tree):
        name = '.'.join(tree)
        return self.words[name]

    def call(self, tree):
        name = tree[0].value
        if name in self.words:
            return self.words[name]
        else:
            return CallWrapper(name, self.words)

    def var(self, tree):
        name = tree[0].value
        if name in self.words:
            vw = self.words[name]
        else:
            vw = VarWrapper(name)
            self.words[name] = vw
        return vw.new

    def word(self, tree):
        name = tree[0].value
        try:
            assert tree[1].type == 'DOCSTR'
            doc = self.string([tree[1].value.lstrip('d')])
            ops = tree[2:]
        except (AssertionError, AttributeError, IndexError):
            doc = None
            ops = tree[1:]
        self.words[name] = WordWrapper(name, ops, doc)
        return EmptyNode

    def import_(self, tree):
        filen = self.string(tree)
        mod_name = os.path.splitext(os.path.basename(filen))[0]
        if not filen.endswith('.bok'):
            filen += '.bok'
        if os.path.isfile(filen):
            path = filen
        else:
            path = os.path.join(LIB_PATH, filen)
        with open(path, 'r') as f:
            text = f.read()
        words = BUILTINS.copy()
        _ = parse_text(text, words)
        uniq_names = set(words) - set(BUILTINS.copy())
        new_words = {
            mod_name+'.'+k: words[k] for k in uniq_names
        }
        self.words.update(new_words)
        return EmptyNode


def parse_text(text, words):
    parser = read_grammar()
    tree = parser.parse(text)
    scope_words(tree)
    dctree = copy.deepcopy(tree)
    code = ReduceTree(words).transform(dctree).children
    code = filter_word_defs(code)
    return code


class Machine:
    def __init__(self):
        self.stack = Stack()
        self.code = Stack()
        self.words = BUILTINS.copy()

    def parse(self, text):
        if text.strip():
            self.code = parse_text(text, self.words)

    def run(self):
        for op in self.code:
            if callable(op):
                op(self.stack)
            else:
                self.stack.push(op)


