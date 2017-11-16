// EBNF grammar for Bok

start : (word | atom)+

word : "(" NAME DOCSTR? (word | atom)* ")"

?atom : SIGNED   -> number
      | STRING   -> string
      | OPERATOR -> operator
      | NAME     -> call
      | "True"   -> true_
      | "False"  -> false_
      | "None"   -> none_
      | var
      | list
      | dot
      | array
      | import_

var : ":" NAME
list : "[" atom* "]"
dot : NAME ("." NAME)+
array : "@" NAME ("." NAME)*
import_ : STRING "import"



// Tokens
OPERATOR : "++" | "+"  | "--" | "-"  | "**" | "*"  | "//" | "/"  | "%"
         | "==" | "!=" | "<=" | ">=" | "<"  | ">"  | "~"
         | "~"  | "&"  | "|"  | "^"  | "<<" | ">>"

NAME : /[a-zA-Z_]\w*/

COMMENT : /\#[^\n]*/
WHITESPACE : /[ \t\f\r\n]+/
%ignore COMMENT
%ignore WHITESPACE


// String literals
DOCSTR : /d/ STRING
STRING : SHORT_STRING | LONG_STRING
SHORT_STRING : /(?i)[ub]?r?("(?!"").*?(?<!\\\\)(\\\\\\\\)*?"|'(?!'').*?(?<!\\\\)(\\\\\\\\)*?')/
LONG_STRING : /(?i)(?s)[ub]?r?(""".*?(?<!\\\\)(\\\\\\\\)*?"""|'''.*?(?<!\\\\)(\\\\\\\\)*?''')/


// Numeric literals
SIGNED : /[+-]?/ NUMBER
NUMBER : IMAG_NUMBER | FLOAT_NUMBER | HEX_NUMBER | OCT_NUMBER | BIN_NUMBER | DEC_NUMBER | ZERO
ZERO : "0"
DEC_NUMBER : /(?i)[1-9]\d*l?/
HEX_NUMBER : /(?i)0x[\da-f]*l?/
OCT_NUMBER : /(?i)0o[0-7]*l?/
BIN_NUMBER : /(?i)0b[0-1]*l?/
FLOAT_NUMBER : /(?i)((\d+\.\d*|\.\d+)(e[-+]?\d+)?|\d+(e[-+]?\d+))/
IMAG_NUMBER : /(?i)\d+j|${FLOAT_NUMBER}j/

