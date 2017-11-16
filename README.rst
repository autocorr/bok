.. class:: no-web

    .. image:: https://raw.githubusercontent.com/autocorr/bok/master/icons/logo_256.png
        :target: https://github.com/autocorr/bok
        :alt: Bok Logo
        :align: center

================
The Bok Language
================

Bok is a dynamic, concatenative programming language.
Inspired by `Joy <http://www.latrobe.edu.au/humanities/research/research-projects/past-projects/joy-programming-language>`_, expressions are written with postfix notation and without formal parameters.
Full lexical scoping is included, so that functions and variables can be grouped together into namespaces, similar to `Reforth <https://github.com/seanpringle/reforth>`_.
The Bok interpreter is written in Python and has a natural interface for calling Python objects and ``numpy`` arrays.
Bok also comes with a full-featured REPL based on `python-prompt-toolkit <https://github.com/jonathanslenders/python-prompt-toolkit/>`_ that includes autocompletion, syntax highlighting, multiline input, history, and a toolbar visualizing the stack.

Documentation on Bok may be found at `ReadTheDocs <https://bok.readthedocs.io>`_, in the ``docs/`` directory of this repository, and within the interpreter through the "help" function.

This is a hobby project designed for exploring programming language concepts and software development practices.
Because the runtime is written in pure Python, it is quite slow, but I suppose if you're using Python in the first place, what's another factor of twenty slower? :)
Bok is named after the astronomer `Bart Bok <https://en.wikipedia.org/wiki/Bart_Bok>`_ who was a pioneer in the study of the Milky Way and discoverer of `Bok globules <https://en.wikipedia.org/wiki/Bok_globule>`_.

Installation
------------
Install with pip by running:

.. code-block::

    pip install git+https://github.com/autocorr/bok.git

Or from the source with:

.. code-block::

    python setup.py install

Requirements
------------
The parser makes use of `Lark <https://github.com/erezsh/lark>`_ to generate rules from an `EBNF <https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form>`_ grammar, which for Bok is written in `grammar.g <https://github.com/autocorr/bok/blob/master/bok/grammar.g>`_.
``prompt_toolkit`` and ``pygments`` are use to create the REPL and provide syntax highlighting, respectively.
``numpy`` is required for array literals and operations, but is otherwise
optional.

.. code-block::

    termcolor          ?
    lark-parser        ?
    prompt_toolkit     ?
    pygments           ?
    numpy (optional)   ?

Getting Started
---------------

.. code-block::

    $ python3 -m bok.repl
    Bok 0.1, type '[<word>] help' for help.
    Hit CTRL+D or type "exit" to quit.
     « # This is a comment
     « # Literals are pushed onto the stack and operated on by functions
     « "Hello, World!" println
    Hello, World!
     « # Functions are defined with ( and )
     « ( think  "." print )
     « # Lists can be used to quote expresions
     « [think] 10 * eval
    ..........
     « ( lfive  [5 <=] [error] ["greater than five" println] if )
     « 4 lfive
    Error: Raised an explicit error.
    Stack dumped
     « # Numpy functions can be called with @
     « 5 @arange dup @cumsum stack
     # [type]    : [value]
     - ndarray   : [ 0  1  3  6 10]
     - ndarray   : [0 1 2 3 4]
     « + println
    [ 0  2  5  9 14]
     « # Try this recursively in python!
     « ( factorial  [1 <] [drop 1] [dup 1 -] [*] linrec )
     « 10000 factorial println
    2846259680917054518906413212119868890148051401702799230794179994274...
     « ^D
    Do you really want to exit ([y]/n)? y

License
-------
Copyright 2017, Brian Svoboda.
This is free software and released under the GNU General Public License (version 3).

