import os
import copy

from lark import Lark, Transformer, Tree
from lark.lexer import Token

from . import array_module
from .stack import BUILTINS, Stack, WordReturn
from .wrappers import EmptyNode, ArrayWr, CallWr, CallWr, VarWr, WordWr


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

    def true(self, tree):
        return True

    def false(self, tree):
        return False

    def none(self, tree):
        return None

    def list(self, tree):
        return list(tree)

    def tuple(self, tree):
        return tuple(tree[0])

    def set(self, tree):
        return set(tree[0])

    def dict(self, tree):
        return dict(tree[0])

    def array(self, tree):
        return array_module.array(tree)

    def arrcall(self, tree):
        obj = array_module
        for child in tree:
            obj = getattr(obj, child)
        if callable(obj):
            return ArrayWr(obj)
        else:
            return obj

    def dot(self, tree):
        name = '.'.join(tree)
        return self.words[name]

    def call(self, tree):
        name = tree[0].value
        if name in self.words:
            return self.words[name]
        else:
            return CallWr(name, self.words)

    def var(self, tree):
        name = tree[0].value
        if name in self.words:
            vw = self.words[name]
        else:
            vw = VarWr(name)
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
        self.words[name] = WordWr(name, ops, doc)
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
    code = [op for op in code if op is not EmptyNode]
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


