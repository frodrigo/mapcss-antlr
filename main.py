import sys
from antlr4 import *
from MapCSSLexer import MapCSSLexer
from MapCSSParser import MapCSSParser
from MapCSSListenerL import MapCSSListenerL, to_mapcss


def main(argv):
    input = FileStream(argv[1], encoding='utf-8')
    lexer = MapCSSLexer(input)
    stream = CommonTokenStream(lexer)
    parser = MapCSSParser(stream)
    tree = parser.stylesheet()

    listener = MapCSSListenerL()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)

    print(to_mapcss(listener.stylesheet))


if __name__ == '__main__':
    main(sys.argv)
