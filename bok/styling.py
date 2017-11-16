#!/usr/bin/env python3

from pygments.style import Style
from pygments.styles.default import DefaultStyle
from pygments.token import (Token, Comment, Number, Keyword,
                            Name, String, Text, Punctuation)
from pygments.lexer import (RegexLexer, include, bygroups, combined, default, words)


class BokStyle(DefaultStyle):
    styles = DefaultStyle.styles
    styles.update({
        Comment: 'italic #808080',
        Number: '#CF7373',
        String: '#8AE234',
        Keyword: '#3465A4',
        Name.Function: '#FCE94F',
        Token.Toolbar: '#ffffff bg:#171717',
    })


class BokLexer(RegexLexer):
    name = 'Bok'
    aliases = ['bok']
    filenames = ['*.bok']
    mimetypes = ['text/x-bok']

    def innerstring_rules(ttype):
        return [
            # the old style '%s' % (...) string formatting (still valid in Py3)
            (r'%(\(\w+\))?[-#0 +]*([0-9]+|[*])?(\.([0-9]+|[*]))?'
             '[hlL]?[E-GXc-giorsux%]', String.Interpol),
            # the new style '{}'.format(...) string formatting
            (r'\{'
             '((\w+)((\.\w+)|(\[[^\]]+\]))*)?'  # field name
             '(\![sra])?'                       # conversion
             '(\:(.?[<>=\^])?[-+ ]?#?0?(\d+)?,?(\.\d+)?[E-GXb-gnosx%]?)?'
             '\}', String.Interpol),

            # backslashes, quotes and formatting signs must be parsed one at a time
            (r'[^\\\'"%{\n]+', ttype),
            (r'[\'"\\]', ttype),
            # unhandled string formatting sign
            (r'%|(\{{1,2})', ttype),
            # newlines are an error (use "nl" state)
        ]

    tokens = {
        'root': [
            (r'#.*$', Comment.Single),
            (r'([(])(\s*)', Text, 'funcname'),
            (r'(?i)([dbr]|dr|db|dbr)(""")',
             bygroups(String.Affix, String.Double), 'tdqs'),
            (r"(?i)([dbr]|dr|db|dbr)(''')",
             bygroups(String.Affix, String.Single), 'tsqs'),
            (r'(?i)([dbr]|dr|db|dbr)(")',
             bygroups(String.Affix, String.Double), 'dqs'),
            (r"(?i)([dbr]|dr|db|dbr)(')",
             bygroups(String.Affix, String.Single), 'sqs'),
            (r'([bB]?)(""")', bygroups(String.Affix, String.Double),
             combined('stringescape', 'tdqs')),
            (r"([bB]?)(''')", bygroups(String.Affix, String.Single),
             combined('stringescape', 'tsqs')),
            (r'([bB]?)(")', bygroups(String.Affix, String.Double),
             combined('stringescape', 'dqs')),
            (r"([bB]?)(')", bygroups(String.Affix, String.Single),
             combined('stringescape', 'sqs')),
            include('keywords'),
            include('numbers'),
            (r'([a-zA-Z_]\w*)', Text),
        ],
        'stringescape': [
            (r'\\([\\abfnrtv"\']|\n|N\{.*?\}|u[a-fA-F0-9]{4}|'
             r'U[a-fA-F0-9]{8}|x[a-fA-F0-9]{2}|[0-7]{1,3})', String.Escape),
        ],
        'strings-single': innerstring_rules(String.Single),
        'strings-double': innerstring_rules(String.Double),
        'dqs': [
            (r'"', String.Double, '#pop'),
            (r'\\\\|\\"|\\\n', String.Escape),  # included here for raw strings
            include('strings-double'),
        ],
        'sqs': [
            (r"'", String.Single, '#pop'),
            (r"\\\\|\\'|\\\n", String.Escape),  # included here for raw strings
            include('strings-single'),
        ],
        'tdqs': [
            (r'"""', String.Double, '#pop'),
            include('strings-double'),
            (r'\n', String.Double),
        ],
        'tsqs': [
            (r"'''", String.Single, '#pop'),
            include('strings-single'),
            (r'\n', String.Single),
        ],
        'keywords': [
            (words((
                'nop', 'not', 'and', 'or', 'bool', 'int', 'float', 'str',
                'read', 'print', 'println', 'stack', 'list', 'listn', 'eval',
                'error', 'assert', 'dump', 'pyeval', 'pyexec', 'pylocals',
                'import', 'exit', 'help'), suffix=r'\b'),
             Keyword),
        ],
        'numbers': [
            (words(('True', 'False', 'None'), suffix=r'\b'), Number),
            (r'(\d+\.\d*|\d*\.\d+)([eE][+-]?[0-9]+)?', Number.Float),
            (r'\d+[eE][+-]?[0-9]+j?', Number.Float),
            (r'0[oO][0-7]+', Number.Oct),
            (r'0[bB][01]+', Number.Bin),
            (r'0[xX][a-fA-F0-9]+', Number.Hex),
            (r'\d+', Number.Integer),
        ],
        'funcname': [
            (r'([a-zA-Z_]\w*)', Name.Function, '#pop'),
            default('#pop'),
        ],
    }


