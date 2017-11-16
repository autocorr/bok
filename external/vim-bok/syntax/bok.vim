" Language:        Bok
" Description:     Vim syntax file for Bok
" Maintainer:      Brian Svoboda
" Latest Revision: October 28, 2017
" GPLv3, the license can be found at https://github.com/autocorr/bok
" Source code from the python-syntax package was used in the expressions for
" strings and numbers. The original repository can be found at:
" https://github.com/hdima/python-syntax/blob/master/syntax/python.vim


if version < 600
	syntax clear
elseif exists("b:current_syntax")
	finish
endif


syn keyword bokKeyword negate not and or read print println stack clear
syn keyword bokKeyword if then else set load assert try except finally
syn keyword bokKeyword error debug
syn keyword bokImport load
syn keyword bokTodo TODO FIXME XXX NOTE contained
syn match   bokComment "#.*$" contains=bokTodo
syn keyword bokType int float str bool
syn keyword bokBoolean True False
syn region  bokFunc start="(" end=")" contains=bokFuncName skipwhite
syn match   bokFuncSym "(" nextgroup=bokFuncName skipwhite
syn match   bokFuncSym ")"
syn match   bokFuncName "[a-zA-Z_][a-zA-Z0-9_]*" display contained

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"                             Strings
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

syn region bokBytes            start=+[bB]'+ skip=+\\\\\|\\'\|\\$+ excludenl end=+'+ end=+$+ keepend contains=bokBytesError,bokBytesContent,@Spell
syn region bokBytes            start=+[bB]"+ skip=+\\\\\|\\"\|\\$+ excludenl end=+"+ end=+$+ keepend contains=bokBytesError,bokBytesContent,@Spell
syn region bokBytes            start=+[bB]"""+ end=+"""+ keepend contains=bokBytesError,bokBytesContent,@Spell
syn region bokBytes            start=+[bB]'''+ end=+'''+ keepend contains=bokBytesError,bokBytesContent,@Spell

syn match bokBytesError        ".\+" display contained
syn match bokBytesContent      "[\u0000-\u00ff]\+" display contained contains=bokBytesEscape,bokBytesEscapeError
syn match bokBytesEscape       +\\[abfnrtv'"\\]+ display contained
syn match bokBytesEscape       "\\\o\o\=\o\=" display contained
syn match bokBytesEscapeError  "\\\o\{,2}[89]" display contained
syn match bokBytesEscape       "\\x\x\{2}" display contained
syn match bokBytesEscapeError  "\\x\x\=\X" display contained
syn match bokBytesEscape       "\\$"

syn match bokUniEscape         "\\u\x\{4}" display contained
syn match bokUniEscapeError    "\\u\x\{,3}\X" display contained
syn match bokUniEscape         "\\U\x\{8}" display contained
syn match bokUniEscapeError    "\\U\x\{,7}\X" display contained
syn match bokUniEscape         "\\N{[A-Z ]\+}" display contained
syn match bokUniEscapeError    "\\N{[^A-Z ]\+}" display contained
syn region bokString           start=+'+ skip=+\\\\\|\\'\|\\$+ excludenl end=+'+ end=+$+ keepend contains=bokBytesEscape,bokBytesEscapeError,bokUniEscape,bokUniEscapeError,@Spell
syn region bokString           start=+"+ skip=+\\\\\|\\"\|\\$+ excludenl end=+"+ end=+$+ keepend contains=bokBytesEscape,bokBytesEscapeError,bokUniEscape,bokUniEscapeError,@Spell
syn region bokString           start=+"""+ end=+"""+ keepend contains=bokBytesEscape,bokBytesEscapeError,bokUniEscape,bokUniEscapeError,@Spell
syn region bokString           start=+'''+ end=+'''+ keepend contains=bokBytesEscape,bokBytesEscapeError,bokUniEscape,bokUniEscapeError,@Spell
syn region bokRawString        start=+[rR]'+ skip=+\\\\\|\\'\|\\$+ excludenl end=+'+ end=+$+ keepend contains=bokRawEscape,@Spell
syn region bokRawString        start=+[rR]"+ skip=+\\\\\|\\"\|\\$+ excludenl end=+"+ end=+$+ keepend contains=bokRawEscape,@Spell
syn region bokRawString        start=+[rR]"""+ end=+"""+ keepend contains=@Spell
syn region bokRawString        start=+[rR]'''+ end=+'''+ keepend contains=@Spell

syn region bokRawBytes         start=+[bB][rR]'+ skip=+\\\\\|\\'\|\\$+ excludenl end=+'+ end=+$+ keepend contains=bokRawEscape,@Spell
syn region bokRawBytes         start=+[bB][rR]"+ skip=+\\\\\|\\"\|\\$+ excludenl end=+"+ end=+$+ keepend contains=bokRawEscape,@Spell
syn region bokRawBytes         start=+[bB][rR]"""+ end=+"""+ keepend contains=@Spell
syn region bokRawBytes         start=+[bB][rR]'''+ end=+'''+ keepend contains=@Spell

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"                             Numbers
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

syn match bokHexError    "\<0[xX]\x*[g-zG-Z]\x*\>" display
syn match bokOctError    "\<0[oO]\=\o*\D\+\d*\>" display
syn match bokBinError    "\<0[bB][01]*\D\+\d*\>" display

syn match bokHexNumber   "\<0[xX]\x\+\>" display
syn match bokOctNumber   "\<0[oO]\o\+\>" display
syn match bokBinNumber   "\<0[bB][01]\+\>" display

syn match bokNumberError "\<\d\+\D\>" display
syn match bokNumberError "\<0\d\+\>" display
syn match bokNumber      "\<\d\>" display
syn match bokNumber      "\<[1-9]\d\+\>" display
syn match bokNumber      "\<\d\+[jJ]\>" display

syn match bokOctError    "\<0[oO]\=\o*[8-9]\d*\>" display
syn match bokBinError    "\<0[bB][01]*[2-9]\d*\>" display

syn match bokFloat       "\.\d\+\%([eE][+-]\=\d\+\)\=[jJ]\=\>" display
syn match bokFloat       "\<\d\+[eE][+-]\=\d\+[jJ]\=\>" display
syn match bokFloat       "\<\d\+\.\d*\%([eE][+-]\=\d\+\)\=[jJ]\=" display

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"                          Highlighting
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

hi def link bokKeyword      Keyword
hi def link bokImport       Include
hi def link bokTodo         Todo
hi def link bokComment      Comment
"hi def link bokFuncDoc      Comment
hi def link bokFuncSym      Text
hi def link bokFuncName     Function
hi def link bokType         Type
hi def link bokBoolean      Boolean
hi def link bokString       String
hi def link bokRawString    String
hi def link bokUniEscape    Special
hi def link bokUniEscapeError Error
hi def link bokBytes        String
hi def link bokRawBytes     String
hi def link bokBytesContent String
hi def link bokBytesError   Error
hi def link bokBytesEscape  Special
hi def link bokBytesEscapeError Error
hi def link bokNumber       Number
hi def link bokHexNumber    Number
hi def link bokOctNumber    Number
hi def link bokBinNumber    Number
hi def link bokFloat        Float
hi def link bokNumberError  Error
hi def link bokOctError     Error
hi def link bokHexError     Error
hi def link bokBinError     Error

let b:current_syntax = "bok"
