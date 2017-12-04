grammar MapCSS;
/*
 * File originally based on https://github.com/Gubaer/dart-mapcss/blob/master/grammar/MapCSS.g
 * GPL 3.0 by Gubaer
 */

tokens {
   STYLESHEET,
   RULE,
   SIMPLE_SELECTOR,
   DESCENDANT_COMBINATOR,
   CHILD_COMBINATOR,
   PARENT_COMBINATOR,
   TYPE_SELECTOR,              // .text is the type
   ZOOM_SELECTOR,
   ATTRIBUTE_SELECTOR,
   CLASS_SELECTOR,
   ROLE_SELECTOR,
   INDEX_SELECTOR,
   PSEUDO_CLASS_SELECTOR,
   LAYER_ID_SELECTOR,         // .text is the layer id
   DECLARATION_BLOCK,
   DECLARATION,

   VALUE_RGB,
   VALUE_RGBA,
   VALUE_URL,
   VALUE_KEYWORD,              // .text is the keyword, without quotes
   VALUE_QUOTED,               // .text is the value (without quotes)
   VALUE_FLOAT,                // .text is the float value
   VALUE_INT,                  // .text is the int value
   VALUE_PERCENTAGE,           // .text is a float or int, *with* trailing %
   VALUE_POINTS,               // .text is a float or int, *with* trailing 'pt'
   VALUE_PIXELS,               // .text is a float or int, *with* trailing 'px'
   VALUE_LIST,
   VALUE_REGEXP,               // .text is a regular expression
   VALUE_INCREMENT,            // .text is the increment

   FUNCTION_CALL,
   PREDICATE,
   TR_CALL,
   EVAL_CALL
}

fragment EBACKSLASH: '\\\\';
fragment UNICODE: '\u0080'..'\uFFFF';

COMMA: ',';
QUESTION_MARK: '?';
OP_INCLUDED_IN: '∈';
OP_INTERSECTS: '⧉';
PAR_OPEN: '(';
PAR_CLOSE: ')';
DOT: '.';

OP_EQ: '=';
OP_NEQ: '!=';
OP_LE: '<=';
OP_GE: '>=';
OP_LT: '<';
OP_GT: '>';
OP_MATCH: '=~';
OP_NOT_MATCH: '!~';
OP_STARTS_WITH: '^=';
OP_ENDS_WITH: '$=';
OP_SUBSTRING: '*=';
OP_CONTAINS: '~=';
OP_OR: '||';
OP_AND: '&&';
OP_MUL: '*';
OP_DIV: '/';
OP_MOD: '%';
OP_PLUS: '+';
OP_MINUS: '-';
OP_NOT: '!'; // NOTE: boolean not -> !(expr)

SET: ('s' | 'S') ('e' | 'E') ('t' | 'T');
ROLE: ('r' | 'R') ('o' | 'O') ('l' | 'L') ('e' | 'E');
INDEX: ('i' | 'I') ('n' | 'N') ('d' | 'D') ('e' | 'E') ('x' | 'X');
IMPORT: '@' ('i' | 'I') ('m' | 'M') ('p' | 'P') ('o' | 'O')('r' | 'R') ('t' | 'T');


fragment DIGIT:  '0'..'9';
fragment CHAR: 'a'..'z' | 'A'..'Z';


/* Basic character sets from CSS specification */
fragment NONASCII: ~('\u0000' .. '\u009F');
fragment NMSTART: 'a'..'z' | 'A'..'Z' | '_' | NONASCII;
fragment NMCHAR: 'a'..'z' | 'A'..'Z' | '_' | '-' | NONASCII;

/* helpers */
NCOMPONENT: (CHAR | '_') (CHAR | DIGIT | '_' | '-')*;


LBRACKET: '[';
RBRACKET: ']';
LBRACE: '{';
RBRACE: '}';
COLON: ':';
SEMICOLON: ';';


/* -------------------- quoted strings -----------------------------------------------------------*/
fragment EDQUOTE: '\\"';
fragment ESQUOTE: '\\\'';
DQUOTED_STRING: '"' (' ' | '!' | '#'..'[' | ']'..'~' | '°' | UNICODE | EDQUOTE | EBACKSLASH)* '"';
SQUOTED_STRING: '\'' (' '..'&' | '('..'[' | ']'..'~' | '°' | UNICODE | ESQUOTE | EBACKSLASH)* '\'';

POSITIVE_INT: [0-9]+;
NEGATIVE_INT: '-' POSITIVE_INT;

POSITIVE_FLOAT: [0-9]+ | [0-9]* '.' [0-9]+;
NEGATIVE_FLOAT: '-' POSITIVE_FLOAT;


/* ----------------------------------------------------------------------------------------------- */
/* Regular expressions  and the '/' operator                                                       */
/* ----------------------------------------------------------------------------------------------- */
fragment REGEX_ESCAPE:   '\\\\' | '\\/' | '\\(' | '\\)'
                       | '\\|' | '\\$' | '\\*' | '\\.' | '\\^' | '\\?' | '\\+' | '\\-'
                       | '\\n' | '\\r' | '\\t'
                       | '\\s' | '\\S'
                       | '\\d' | '\\D'
                       | '\\w' | '\\W';
fragment REGEX_START:  ' '..')' | '+'..'.' |'0'..'[' | ']'..'~' | '°' | UNICODE | REGEX_ESCAPE;
fragment REGEX_CHAR:  ' '..'.' |'0'..'[' | ']'..'~' | '°' | UNICODE | REGEX_ESCAPE;

REGEXP: '/' REGEX_START REGEX_CHAR* '/';


/* ----------------------------------------------------------------------------------------------- */
/* Whitespace and comments                                                                         */
/* ----------------------------------------------------------------------------------------------- */
WS:           (' ' | '\t' | '\n' | '\r' | '\f') -> channel(HIDDEN);
SL_COMMENT:   '//' .*? '\r'? '\n' -> channel(HIDDEN);
ML_COMMENT:   '/*'  .*? '*/' -> channel(HIDDEN);


/* =============================================================================================== */
/* Grammar                                                                                         */
/* ===============================================================================================  */

stylesheet
    : entry* EOF
    ;

entry
    : rule_
/*    | import_statement*/
    ;

rule_
    : selector (COMMA selector)* COMMA* declaration_block
    ;

selector
    : simple_selector
    | simple_selector simple_selector
    | simple_selector OP_GT (link_selector | pseudo_class_selector)* simple_selector
    | simple_selector simple_selector_operator simple_selector
    ;

simple_selector_operator : OP_LT | OP_INCLUDED_IN | OP_INTERSECTS;

link_selector
    : LBRACKET ROLE binary_operator predicate_primitive RBRACKET
    | LBRACKET INDEX op=int_operator v=int_ RBRACKET
    ;

layer_id_selector
    : COLON COLON k=cssident
    ;

int_operator : OP_EQ | OP_NEQ | OP_LT | OP_LE | OP_GT | OP_GE;

simple_selector
    : type_selector (class_selector | attribute_selector | pseudo_class_selector)* layer_id_selector?
    ;

quoted
    : DQUOTED_STRING
    | SQUOTED_STRING
    ;

cssident
    : '-' ?  NCOMPONENT
    ;

osmtag
    : '-' ?  NCOMPONENT ((':'|'.') NCOMPONENT)*
    ;

attribute_selector
    : LBRACKET predicate RBRACKET
    ;

predicate
    : predicate_simple
    | predicate_operator
    | predicate_function
    ;

predicate_simple
    : OP_NOT ? predicate_ident QUESTION_MARK ?
    | OP_NOT ? quoted          QUESTION_MARK ?
    | OP_NOT ? rhs_match
    ;

predicate_operator
    : predicate_primitive binary_operator predicate_primitive
    | predicate_primitive (OP_MATCH | OP_NOT_MATCH) rhs_match
    ;

predicate_function
    : cssident PAR_OPEN (predicate_function_param (COMMA predicate_function_param)*)? PAR_CLOSE
    ;

predicate_function_param
    : single_value
    | predicate_function
    ;

predicate_ident
    : osmtag
    ;

predicate_primitive
    : single_value
    | predicate_ident
    | predicate_function
    ;

rhs_match
    : quoted
    | r=REGEXP
    ;

binary_operator
    : OP_EQ | OP_NEQ | OP_LT | OP_GT | OP_LE
    | OP_GE | OP_STARTS_WITH | OP_ENDS_WITH | OP_SUBSTRING
    | OP_CONTAINS
    ;

class_selector
    : OP_NOT DOT cssident
    | DOT cssident
    ;

pseudo_class_selector
    : COLON OP_NOT cssident
    | OP_NOT COLON cssident
    | COLON cssident
    ;

type_selector
    : cssident
    | OP_MUL
    ;

declaration_block
    :  l=LBRACE declarations RBRACE
    |  l=LBRACE RBRACE
    ;

declarations
    : declaration (SEMICOLON declaration)* SEMICOLON*
    ;

declaration
    : SET DOT ? cssident
    | declaration_property COLON declaration_value
    ;

declaration_property
    : cssident
    ;

declaration_value
    : declaration_value_single
/*    | EVAL  PAR_OPEN expr PAR_CLOSE*/
    | declaration_value_function
    ;

declaration_value_single
    : single_value
    ;

declaration_value_function
    : cssident PAR_OPEN (declaration_value (COMMA declaration_value)*)? PAR_CLOSE
    ;

int_
    : n=POSITIVE_INT
    | n=NEGATIVE_INT
    ;

num
    : n=POSITIVE_INT
    | n=NEGATIVE_INT
    | n=POSITIVE_FLOAT
    | n=NEGATIVE_FLOAT
    ;

single_value
    : v=POSITIVE_INT
    | v=NEGATIVE_INT
    | v=POSITIVE_FLOAT
    | v=NEGATIVE_FLOAT
    | quoted
/*    | declaration_value_function*/
    /* make sure these are the last alternatives in this rule */
    | osmtag
    ;

/* ------------------------------------------------------------------------------------------ */
/* eval expressions                                                                           */
/* ------------------------------------------------------------------------------------------ */
expr
    : logicalExpression
    ;

args
    : (expr (COMMA expr)*)?
    ;

logicalExpression
    : booleanAndExpression (
            OP_OR logicalExpression
          |
      )
    ;

booleanAndExpression
    :    equalityExpression (
           |
         )
    ;

equalityExpression
    : relationalExpression (
            OP_EQ  relationalExpression
          | OP_NEQ relationalExpression
          |
      )
    ;

relationalExpression
    : additiveExpression (
            OP_LT additiveExpression
          | OP_LE additiveExpression
          | OP_GT additiveExpression
          | OP_GE additiveExpression
          |
      )
    ;

additiveExpression
    : multiplicativeExpression (
            OP_PLUS  additiveExpression
          | OP_MINUS additiveExpression
          |
      )
    ;

multiplicativeExpression
    : unaryExpression (
          (OP_MUL multiplicativeExpression)
        | (OP_DIV multiplicativeExpression)
        | (OP_MOD multiplicativeExpression)
        |
      )
    ;

unaryExpression
    : OP_NOT primaryExpression
    | primaryExpression
    ;

primaryExpression
    : PAR_OPEN expr PAR_CLOSE
    | f=cssident PAR_OPEN args PAR_CLOSE
    | v=POSITIVE_FLOAT
    | v=POSITIVE_INT
    | v=NEGATIVE_FLOAT
    | v=NEGATIVE_INT
    | quoted
    | osmtag
    ;
