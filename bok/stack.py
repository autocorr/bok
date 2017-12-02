#!/usr/bin/env python3

import sys
import textwrap
from collections import deque, Iterable

from termcolor import colored


class RaisedError(Exception):
    pass


class WordReturn(Exception):
    pass


class Stack(deque):
    __doc__ = None
    push = deque.append
    pushleft = deque.appendleft

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pylocals = {}
        self.args = []
        self.kwargs = {}

    @property
    def args_loaded(self):
        return self.args or self.kwargs

    def clear_args(self):
        self.args.clear()
        self.kwargs.clear()

    def top_to_stack(self):
        try:
            return Stack([self[-1]])
        except IndexError:
            return Stack([])

    def take_n_to_stack(self, n):
        return self[:-n].copy()

    def call_quote(self, quote):
        for op in quote:
            if callable(op):
                op(self)
            else:
                self.push(op)

    def apply_to_top(self, quote):
        sub_stack = self.top_to_stack()
        sub_stack.call_quote(quote)
        return sub_stack[-1]


#---------------------------------------------------------------------------
#                            Numeric Operators
#---------------------------------------------------------------------------

def nop(stack):
    """
    (  --  )

    No operation, pass.
    """
    pass


def negate(stack):
    """
    ( x -- y )

    Negate the element.

    Examples
    --------
    « 1 negate println
    -1
    """
    stack[-1] = -stack[-1]


def plus(stack):
    """
    ( x y -- z )
    ( [a] [b] -- [a b] )

    Add two elements. For numeric types, this performs arithmetic
    addition. For lists and strings, this performs concatentation.

    Examples
    --------
    « 1 1 + println
    2
    « [1 2] [3] + println
    [1, 2, 3]
    """
    stack[-2] = stack[-2] + stack[-1]
    stack.pop()


def increment(stack):
    """( x -- x+1 )"""
    stack[-1] += 1


def minus(stack):
    """
    ( x y -- z )

    Subtract two elements.
    """
    stack[-2] = stack[-2] - stack[-1]
    stack.pop()


def decrement(stack):
    """( x -- x-1 )"""
    stack[-1] -= 1


def mul(stack):
    """
    ( x y -- z )
    ( [a] n -- [a a ..] )

    Multiply two elements. For numeric types this peforms arithmetic
    multiplication. For a list and integer this duplicates then
    concatenates.

    Examples
    --------
    « 2 3 * println
    6
    « [1] 3 * println
    [1, 1, 1]
    """
    stack[-2] = stack[-2] * stack[-1]
    stack.pop()


def power(stack):
    """( x y -- x**y )"""
    stack[-2] = stack[-2]**stack[-1]
    stack.pop()


def div(stack):
    """( x y -- z )"""
    stack[-2] = stack[-2] / stack[-1]
    stack.pop()


def floor_div(stack):
    """( x y -- z )"""
    stack[-2] = stack[-2] // stack[-1]
    stack.pop()


def mod(stack):
    """( x y -- z )"""
    stack[-2] = stack[-2] % stack[-1]
    stack.pop()


#---------------------------------------------------------------------------
#                             Bitwise Operators
#---------------------------------------------------------------------------

def bit_not(stack):
    """( i j -- k )"""
    stack[-1] = ~stack[-1]


def bit_and(stack):
    """( i j -- k )"""
    stack[-2] = stack[-2] & stack[-1]
    stack.pop()


def bit_or(stack):
    """( i j -- k )"""
    stack[-2] = stack[-2] | stack[-1]
    stack.pop()


def bit_xor(stack):
    """( i j -- k )"""
    stack[-2] = stack[-2] ^ stack[-1]
    stack.pop()


def bit_lshift(stack):
    """( i j -- k )"""
    stack[-2] = stack[-2] << stack[-1]
    stack.pop()


def bit_rshift(stack):
    """( i j -- k )"""
    stack[-2] = stack[-2] >> stack[-1]
    stack.pop()


#---------------------------------------------------------------------------
#                           Comparison Operators
#---------------------------------------------------------------------------

def eq(stack):
    """( a b -- ? )"""
    stack[-2] = stack[-2] == stack[-1]
    stack.pop()


def ne(stack):
    """( a b -- ? )"""
    stack[-2] = stack[-2] != stack[-1]
    stack.pop()


def gt(stack):
    """( a b -- ? )"""
    stack[-2] = stack[-2] > stack[-1]
    stack.pop()


def ge(stack):
    """( a b -- ? )"""
    stack[-2] = stack[-2] >= stack[-1]
    stack.pop()


def lt(stack):
    """( a b -- ? )"""
    stack[-2] = stack[-2] < stack[-1]
    stack.pop()


def le(stack):
    """( a b -- ? )"""
    stack[-2] = stack[-2] <= stack[-1]
    stack.pop()


#---------------------------------------------------------------------------
#                             Logical Operators
#---------------------------------------------------------------------------

def not_(stack):
    """( a -- ? )"""
    stack[-1] = not stack[-1]


def and_(stack):
    """( a b -- c )"""
    stack[-2] = stack[-2] and stack[-1]
    stack.pop()


def or_(stack):
    """( a b -- c )"""
    stack[-2] = stack[-2] or stack[-1]
    stack.pop()


def xor(stack):
    """( a b -- c )"""
    a = stack[-2]
    b = stack[-1]
    stack[-2] = (not a and b) or (not b and a)
    stack.pop()


#---------------------------------------------------------------------------
#                    Python Function Argument Operators
#---------------------------------------------------------------------------

def append_args(stack):
    stack.args.append(stack.pop())


def append_kwargs(stack):
    stack.kwargs.update(stack.pop())


#---------------------------------------------------------------------------
#                            Python Builtins
#---------------------------------------------------------------------------

def abs_(stack):
    stack[-1] = abs(stack[-1])


def all_(stack):
    stack[-1] = all(stack[-1])


def any_(stack):
    stack[-1] = any(stack[-1])


def ascii_(stack):
    stack[-1] = ascii(stack[-1])


def bin_(stack):
    stack[-1] = bin(stack[-1])


def chr_(stack):
    stack[-1] = chr(stack[-1])


def hash_(stack):
    stack[-1] = hash(stack[-1])


def len_(stack):
    stack[-1] = len(stack[-1])


def max_(stack):
    stack[-1] = max(*stack[-1])


def min_(stack):
    stack[-1] = min(*stack[-1])


def repr_(stack):
    stack[-1] = repr(stack[-1])


def sum_(stack):
    stack[-1] = sum(stack[-1])


def reversed_(stack):
    stack[-1] = reversed(stack[-1])


#---------------------------------------------------------------------------
#                            Stack Shufflers
#---------------------------------------------------------------------------

def drop(stack):
    """( a --  )"""
    stack.pop()


def drop2(stack):
    """( a b --  )"""
    stack.pop()
    stack.pop()


def dup(stack):
    """( a -- a a )"""
    stack.push(stack[-1])


def swap(stack):
    """( a b -- b a )"""
    stack[-2], stack[-1] = stack[-1], stack[-2]


def over(stack):
    """( a b -- a b a )"""
    stack.push(stack[-2])


def rollup(stack):
    """( a b c -- c a b )"""
    stack[-3], stack[-2], stack[-1] = stack[-1], stack[-3], stack[-2]


def rolldown(stack):
    """( a b c -- b c a )"""
    stack[-3], stack[-2], stack[-1] = stack[-2], stack[-1], stack[-3]


def rotate(stack):
    """( a b c -- c b a )"""
    stack[-3], stack[-1] = stack[-1], stack[-3]


def nip(stack):
    """( a b -- b)"""
    stack[-2] = stack[-1]
    stack.pop()


def tuck(stack):
    """( a b -- b a b )"""
    stack.insert(-2, foo[-1])


#---------------------------------------------------------------------------
#                             Types and Casting
#---------------------------------------------------------------------------

def cast_bool(stack):
    """( a -- ? )"""
    stack[-1] = bool(stack[-1])


def cast_int(stack):
    """( a -- i )"""
    stack[-1] = int(stack[-1])


def cast_float(stack):
    """( a -- f )"""
    stack[-1] = float(stack[-1])


def cast_str(stack):
    """( a -- s )"""
    stack[-1] = str(stack[-1])


#---------------------------------------------------------------------------
#                                Printing
#---------------------------------------------------------------------------

def input_(stack):
    """(  -- s )"""
    stack.push(input())


def print_(stack):
    """( a --  )"""
    sys.stdout.write(str(stack.pop()))
    sys.stdout.flush()


def println(stack):
    """( a --  )"""
    sys.stdout.write('{0}\n'.format(stack.pop()))
    sys.stdout.flush()


def print_stack(stack):
    """(  --  )"""
    green = lambda s : colored(s, 'green')
    if not stack:
        print(' # (empty)')
    else:
        print(' # ['+green('type')+']     : ['+green('value')+']')
        for val in reversed(stack):
            name = type(val).__name__
            if name in ('module', 'function'):
                s = val.__name__
            else:
                s = str(val)
            if '\n' in s:
                s = s.replace('\n', '\n'+16*' ')
            print(' - {0:10} : {1}'.format(name, s))


#---------------------------------------------------------------------------
#                            Data Structures
#---------------------------------------------------------------------------

def set_(stack):
    stack[-1] = set(stack[-1])


def tuple_(stack):
    stack[-1] = tuple(stack[-1])


def list_(stack):
    """( a -- [a] )"""
    stack[-1] = list([stack[-1]])


def list2(stack):
    """( a b -- [a b] )"""
    item2 = stack.pop()
    item1 = stack.pop()
    stack.push([item1, item2])


def list3(stack):
    """( a b c -- [a b c] )"""
    item3 = stack.pop()
    item2 = stack.pop()
    item1 = stack.pop()
    stack.push([item1, item2, item3])


def listn(stack):
    """( .. n -- [..][n] )"""
    n = stack.pop()
    quote = list(stack.pop() for _ in range(n))
    quote.reverse()
    stack.push(quote)


def append(stack):
    """( [..] a -- [.. a])"""
    value = stack.pop()
    quote = stack[-1]
    quote.append(value)


def extend(stack):
    """( [..] [a b ..] -- [.. a b ..])"""
    value = stack.pop()
    quote = stack[-1]
    quote.extend(value)


def prepend(stack):
    """( [..] a -- [a ..] )"""
    value = stack.pop()
    quote = stack[-1]
    quote.insert(0, value)


def range_(stack):
    """
    ( end -- [0 .. end-1] )
    ( [end] -- [0 .. end-1] )
    ( [start end] -- [start .. end-1] )
    ( [start end step] -- [start .. start+step .. end-1] )
    """
    value = stack[-1]
    if isinstance(value, Iterable):
        range_iter = range(*value)
    else:
        range_iter = range(value)
    stack[-1] = range_iter


#---------------------------------------------------------------------------
#                            Data Structures
#---------------------------------------------------------------------------

def exec_(stack):
    """( [..] -- .. )"""
    stack.call_quote(stack.pop())


def error(stack):
    """( -- ! )"""
    raise RaisedError("Raised an explicit error.")


def assert_(stack):
    """( ? -- !|None )"""
    assert stack.pop()


def dump(stack):
    """( .. --  )"""
    stack.clear()


#---------------------------------------------------------------------------
#                 Higher-order Functions and Combinators
#---------------------------------------------------------------------------

def map_(stack):
    """( [a ..] -- [f(a) ..] )"""
    quote = stack.pop()
    iterable  = stack[-1]
    res_stack = Stack()
    for ii, value in enumerate(iterable):
        sub_stack = Stack([value])
        sub_stack.call_quote(quote)
        res_stack.push(sub_stack.pop())
    stack[-1] = list(res_stack)


def filter_(stack):
    quote = stack.pop()
    iterable  = stack.pop()
    res_stack = Stack()
    sub_stack = Stack()
    for value in iterable:
        sub_stack.push(value)
        sub_stack.call_quote(quote)
        if sub_stack.pop():
            res_stack.push(value)
        sub_stack.clear()
    stack.push(list(res_stack))


def fold(stack):
    quote = stack.pop()
    initial = stack.pop()
    iterable = stack.pop()
    stack.push(initial)
    for value in iterable:
        stack.push(value)
        stack.call_quote(quote)


def dip(stack):
    quote = stack.pop()
    value = stack.pop()
    stack.call_quote(quote)
    stack.push(value)


def keep(stack):
    quote = stack.pop()
    value = stack[-1]
    stack.call_quote(quote)
    stack.push(value)


def bi(stack):
    q2 = stack.pop()
    q1 = stack.pop()
    value = stack.pop()
    stack.push(value)
    stack.call_quote(q1)
    stack.push(value)
    stack.call_quote(q2)


def tri(stack):
    q3 = stack.pop()
    q2 = stack.pop()
    q1 = stack.pop()
    value = stack.pop()
    stack.push(value)
    stack.call_quote(q1)
    stack.push(value)
    stack.call_quote(q2)
    stack.push(value)
    stack.call_quote(q3)


def cleave(stack):
    q2 = stack.pop()
    q1 = stack.pop()
    v2 = stack.pop()
    v1 = stack.pop()
    stack.push(v1)
    stack.call_quote(q1)
    stack.push(v2)
    stack.call_quote(q2)


def linrec(stack):
    post_q = stack.pop()
    else_q = stack.pop()
    true_q = stack.pop()
    cond_q = stack.pop()
    n_passes = 0
    while True:
        condition = stack.apply_to_top(cond_q)
        if condition:
            stack.call_quote(true_q)
            break
        else:
            stack.call_quote(else_q)
        n_passes += 1
    for _ in range(n_passes):
        stack.call_quote(post_q)


def while_(stack):
    body_q = stack.pop()
    stop_q = stack.pop()
    while True:
        condition = stack.apply_to_top(stop_q)
        if not condition:
            break
        stack.call_quote(body_q)


def foreach(stack):
    quote = stack.pop()
    iterable = stack.pop()
    for value in iterable:
        stack.push(value)
        stack.call_quote(quote)


def repeat(stack):
    quote = stack.pop()
    n = stack.pop()
    for _ in range(n):
        stack.call_quote(quote)


def choice(stack):
    false_value = stack.pop()
    true_value  = stack.pop()
    condition   = stack.pop()
    if condition:
        stack.push(true_value)
    else:
        stack.push(false_value)


def if_(stack):
    false_clause = stack.pop()
    true_clause  = stack.pop()
    cond_clause  = stack.pop()
    condition = stack.apply_to_top(cond_clause)
    if condition:
        stack.call_quote(true_clause)
    else:
        stack.call_quote(false_clause)


def when(stack):
    true_clause = stack.pop()
    cond_clause = stack.pop()
    condition = stack.apply_to_top(cond_clause)
    if condition:
        stack.call_quote(true_clause)


def unless(stack):
    false_clause = stack.pop()
    cond_clause  = stack.pop()
    condition = stack.apply_to_top(cond_clause)
    if not condition:
        stack.call_quote(false_clause)


def cond(stack):
    pred_expr_pairs = stack.pop()
    for pred, expr in pred_expr_pairs:
        if stack.apply_to_top(pred):
            stack.call_quote(expr)
            break


def slice_(stack):
    stack[-1] = slice(*stack[-1])


def get_from(stack):
    where = stack.pop()
    obj = stack[-1]
    stack.push(obj[where])


def set_to(stack):
    where = stack.pop()
    items = stack.pop()
    obj = stack[-1]
    obj[where] = items


def help_(stack):
    quote = stack.pop()
    if not isinstance(quote, list):
        raise RuntimeError('help must take a quotation')
    if not quote:
        raise RuntimeError('help passed an empty list')
    obj = quote[0]
    docstring = obj.__doc__
    if docstring is None and hasattr(obj, '__name__'):
        print('"{0}" has no docstring available'.format(obj.__name__))
    elif docstring is None:
        print('type "{0}" has no docstring available'.format(type(obj)))
    else:
        print(textwrap.dedent(docstring))


def return_(stack):
    raise WordReturn


def pyeval(stack):
    stack[-1] = eval(stack[-1], stack.pylocals)


def pyexec(stack):
    exec(stack.pop(), stack.pylocals)


def print_pylocals(stack):
    for k, v in stack.pylocals.items():
        if k == '__builtins__':
            continue
        print(k, '=', v)


def exit(stack):
    sys.exit(0)


BUILTINS = {
    '!=':       ne,
    '%':        mod,
    '&':        bit_and,
    '*':        mul,
    '**':       power,
    '+':        plus,
    '++':       increment,
    '-':        minus,
    '--':       decrement,
    '/':        div,
    '//':       floor_div,
    '<':        lt,
    '<<':       bit_lshift,
    '<=':       le,
    '==':       eq,
    '>':        gt,
    '>*':       append_args,
    '>**':      append_kwargs,
    '>=':       ge,
    '>>':       bit_rshift,
    '^':        bit_xor,
    'abs':      abs_,
    'all':      all_,
    'and':      and_,
    'any':      any_,
    'append':   append,
    'ascii':    ascii_,
    'assert':   assert_,
    'assign':   set_to,
    'bi':       bi,
    'bin':      bin_,
    'bool':     cast_bool,
    'choice':   choice,
    'chr':      chr_,
    'cleave':   cleave,
    'cond':     cond,
    'dip':      dip,
    'drop':     drop,
    'drop2':    drop2,
    'dump':     dump,
    'dup':      dup,
    'error':    error,
    'exec':     exec_,
    'exit':     exit,
    'extend':   extend,
    'filter':   filter_,
    'float':    cast_float,
    'fold':     fold,
    'foreach':  foreach,
    'get':      get_from,
    'hash':     hash_,
    'help':     help_,
    'if':       if_,
    'input':    input_,
    'int':      cast_int,
    'keep':     keep,
    'len':      len_,
    'linrec':   linrec,
    'list':     list_,
    'list2':    list2,
    'list3':    list3,
    'listn':    listn,
    'map':      map_,
    'max':      max_,
    'min':      min_,
    'negate':   negate,
    'nip':      nip,
    'nop':      nop,
    'not':      not_,
    'or':       or_,
    'over':     over,
    'prepend':  prepend,
    'print':    print_,
    'println':  println,
    'pyeval':   pyeval,
    'pyexec':   pyexec,
    'pylocals': print_pylocals,
    'range':    range_,
    'repeat':   repeat,
    'repr':     repr_,
    'return':   return_,
    'rolldown': rolldown,
    'rollup':   rollup,
    'rotate':   rotate,
    'set':      set_,
    'slice':    slice_,
    'stack':    print_stack,
    'str':      cast_str,
    'sum':      sum_,
    'swap':     swap,
    'tri':      tri,
    'tuck':     tuck,
    'tuple':    tuple_,
    'unless':   unless,
    'when':     when,
    'while':    while_,
    'xor':      xor,
    '|':        bit_or,
    '~':        bit_not,
}


