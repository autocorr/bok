#!/usr/bin/env python3

import os

from termcolor import colored
from prompt_toolkit import prompt
from prompt_toolkit.keys import Keys
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.history import FileHistory, InMemoryHistory
from prompt_toolkit.key_binding.manager import KeyBindingManager
from lark.lexer import UnexpectedInput
from lark.common import UnexpectedToken
from pygments.token import Token

from .parser import Machine
from .stack import RaisedError
from .styling import BokStyle, BokLexer


try:
    HIST_FILEN = '~/.bok_history'
    HISTORY = FileHistory(os.path.expanduser(HIST_FILEN))
except:
    HISTORY = InMemoryHistory()


def get_completer(machine):
    matchables = set(
        k.split('.')[0]
        for k in machine.words.keys()
        if k[0].isalnum()
    )
    completer = WordCompleter(matchables)
    return completer


def get_toolbar(machine):
    stack_items = [str(ii) for ii in machine.stack]
    line = ' | '.join(stack_items).replace('\n','').replace('\t','')
    if len(line) > 73:
        line = '... {0}'.format(line[-63:])
    top_txt = ' [top]' if stack_items else ''
    msg = 'stack: {0}{1}'.format(line, top_txt)
    def get_tokens(cli):
        return [(Token.Toolbar, msg)]
    return get_tokens


def get_continuation_tokens(cli, width):
        return [(Token, ' . ')]


def get_bindings():
    key_bindings_manager = KeyBindingManager.for_prompt()
    def insert_pair(l_symb, r_symb):
        @key_bindings_manager.registry.add_binding(l_symb)
        def _(event):
            buf = event.cli.current_buffer
            buf.insert_text(l_symb+r_symb)
            buf.cursor_left(count=1)
    def insert_spaced_pair(l_symb, r_symb):
        @key_bindings_manager.registry.add_binding(l_symb, ' ')
        def _(event):
            buf = event.cli.current_buffer
            buf.insert_text(l_symb+'  '+r_symb)
            buf.cursor_left(count=2)
    def undo_add_pair(l_symb, r_symb):
        @key_bindings_manager.registry.add_binding(l_symb, Keys.Backspace)
        def _(event):
            return
    def pass_closing_pair(l_symb, r_symb):
        @key_bindings_manager.registry.add_binding(r_symb)
        def _(event):
            buf = event.cli.current_buffer
            text = buf.text[buf.cursor_position:]
            if text.lstrip().startswith(r_symb):
                symb_ix = text.find(r_symb) + 1
                buf.cursor_right(count=symb_ix)
            else:
                buf.insert_text(r_symb)
                buf.cursor_right(count=1)
    parens = [('(', ')'), ('[', ']')]
    for pair in parens:
        insert_pair(*pair)
        insert_spaced_pair(*pair)
        undo_add_pair(*pair)
        pass_closing_pair(*pair)
    @key_bindings_manager.registry.add_binding(Keys.F4)
    def _(event):
        buf = event.cli.current_buffer
        buf.insert_text('dump')
        buf.newline()
    return key_bindings_manager


def bok_prompt(machine):
    completer = get_completer(machine)
    toolbar = get_toolbar(machine)
    key_bindings_manager = get_bindings()
    source = prompt(
        ' « ',
        mouse_support=True,
        history=HISTORY,
        completer=completer,
        complete_while_typing=False,
        display_completions_in_columns=True,
        lexer=BokLexer,
        style=BokStyle,
        get_bottom_toolbar_tokens=toolbar,
        get_continuation_tokens=get_continuation_tokens,
        #vi_mode=True,
        #multiline=True,
        key_bindings_registry=key_bindings_manager.registry,
    )
    return source


def repl():
    print('Bok 0.1, type "[<word>] help" for help.')
    print('Hit CTRL+D or type "exit" to quit.')
    red_err = colored('Error:', 'red')
    m = Machine()
    while True:
        try:
            source = bok_prompt(m)
            m.parse(source)
            m.run()
        except (RaisedError, RuntimeError, KeyError, IndexError) as e:
            print(red_err, e)
            print(colored('Stack dumped', 'red'))
            m.stack.clear()
        except UnexpectedToken as e:
            msg = 'Unexpected token {e.token} at ({e.line}, {e.column})'
            print(red_err, msg.format(e=e))
        except UnexpectedInput as e:
            msg = 'Unexpected input at ({e.line}, {e.column})'
            print(red_err, msg.format(e=e))
        except SystemExit:
            break
        except (KeyboardInterrupt, EOFError):
            while True:
                resp = input('Do you really want to exit ([y]/n)? ')
                resp = resp.lower()
                if resp in ('', 'y', 'n'):
                    break
            if resp == 'n':
                continue
            else:
                break


if __name__ == '__main__':
    repl()


