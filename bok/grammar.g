// EBNF grammar for Bok

start : (word | atom)+

word : "(" NAME DOCSTR? (word | atom)* ")"

?atom : SIGNED    -> number
      | STRING    -> string
      | OPERATOR  -> operator
      | NAME      -> call
      | "True"    -> true
      | "False"   -> false
      | "None"    -> none
      | ":" NAME  -> var
      | STRING "import"      -> import_
      | NAME ("." NAME)+     -> dot
      | "@" NAME ("." NAME)* -> arrcall
      | list
      | "{" atom* "}"        -> array
      | "T" list             -> tuple
      | "S" list             -> set

list : "[" atom* "]"
//dict_pair : (SIGNED | STRING | tuple) atom
//dict : "M" "[" ( dict_pair ",")* (dict_pair (",")?)? "]"



// Tokens
OPERATOR : "++" | "+"  | "--" | "-"
         | "**" | "*"  | "//" | "/"  | "%"
         | ">**"| ">*"
         | "~"  | "&"  | "|"  | "^"  | "<<" | ">>"
         | "==" | "!=" | "<=" | ">=" | "<"  | ">"

NAME : /[a-zA-Z_]\w*/

COMMENT : /#[^\n]*/
WHITESPACE : /[ \t\f\r\n]+/
%ignore COMMENT
%ignore WHITESPACE


// String literals
DOCSTR : /d/ STRING
STRING : SHORT_STRING | LONG_STRING
SHORT_STRING : /(?i)[ub]?r?("(?!"").*?(?<!\\\\)(\\\\\\\\)*?"|'(?!'').*?(?<!\\\\)(\\\\\\\\)*?')/
LONG_STRING : /(?i)(?s)[ub]?r?(""".*?(?<!\\\\)(\\\\\\\\)*?"""|'''.*?(?<!\\\\)(\\\\\\\\)*?''')/
//SHORT_STRING : /[ubf]?r?("(?!"").*?(?<!\\)(\\\\)*?"|'(?!'').*?(?<!\\)(\\\\)*?')/i
//LONG_STRING : /[ubf]?r?(""".*?(?<!\\)(\\\\)*?"""|'''.*?(?<!\\)(\\\\)*?''')/is


// Numeric literals
SIGNED : /[+-]?/ NUMBER
NUMBER : IMAG_NUMBER | FLOAT_NUMBER | HEX_NUMBER | OCT_NUMBER | BIN_NUMBER | DEC_NUMBER | ZERO
ZERO : /0/
DEC_NUMBER : /(?i)[1-9]\d*/
HEX_NUMBER : /(?i)0x[\da-f]*/
OCT_NUMBER : /(?i)0o[0-7]*/
BIN_NUMBER : /(?i)0b[0-1]*/
FLOAT_NUMBER : /(?i)((\d+\.\d*|\.\d+)(e[-+]?\d+)?|\d+(e[-+]?\d+))/
IMAG_NUMBER : /(?i)\d+j|${FLOAT_NUMBER}j/
//DEC_NUMBER : /[1-9]\d*/i
//HEX_NUMBER : /0x[\da-f]*/i
//OCT_NUMBER : /0o[0-7]*/i
//BIN_NUMBER : /0b[0-1]*/i
//FLOAT_NUMBER : /((\d+\.\d*|\.\d+)(e[-+]?\d+)?|\d+(e[-+]?\d+))/i
//IMAG_NUMBER : /\d+j|${FLOAT_NUMBER}j/i
