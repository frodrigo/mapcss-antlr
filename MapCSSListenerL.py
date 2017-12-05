from MapCSSListener import MapCSSListener
from MapCSSParser import MapCSSParser


def to_mapcss(t):
    if isinstance(t, str):
        return t
    elif t['type'] == 'stylesheet':
        return "\n".join(map(to_mapcss, t['rules']))
    elif t['type'] == 'rule':
        return ",\n".join(map(to_mapcss, t['selectors'])) + " {\n    " + "\n    ".join(map(to_mapcss, t['declarations'])) + "\n}\n"
    elif t['type'] == 'selector':
        if t['operator']:
            return (
                to_mapcss(t['simple_selectors'][0]) + " " +
                t['operator'] +
                "".join(map(to_mapcss, t['link_selectors'])) +
                "".join(map(to_mapcss, t['pseudo_class'])) + " " +
                to_mapcss(t['simple_selectors'][1])
            )
        else:
            return "".join(map(to_mapcss, t['simple_selectors']))
    elif t['type'] == 'link_selector':
        if t['role']:
            return "[role" + t['operator'] + to_mapcss(t['role']) + "]"
        else: # t['index']
            return "[index" + t['operator'] + to_mapcss(t['index']) + "]"
    elif t['type'] == 'simple_selector':
        return (
            to_mapcss(t['type_selector']) +
            "".join(map(to_mapcss, t['class_selectors'])) +
            "".join(map(lambda a: "[" + to_mapcss(a) + "]", t['predicates'])) +
            "".join(map(to_mapcss, t['pseudo_class']))
        )
    elif t['type'] == 'class_selector':
        return ("!" if t['not'] else "") + "." + t['class']
    elif t['type'] == 'predicate_simple':
        return ("!" if t['not'] else "") + t['predicate'] + ("?" if t['question_mark'] else "")
    elif t['type'] == 'pseudo_class':
        return (
            ("!" if t['not_class'] else "") +
            ":" + t['pseudo_class']
        )
    elif t['type'] == 'declaration':
        if t['set']:
            return "set " + t['set'] + ";"
        else:
            return to_mapcss(t['property']) + ": " + to_mapcss(t['value']) + ";"
    elif t['type'] == 'declaration_value_single':
        return to_mapcss(t['value'])
    elif t['type'] == 'declaration_value_function':
        return t['name'] + "(" + ", ".join(map(to_mapcss, t['params'])) + ")"
    elif t['type'] == 'booleanExpression':
        if t['operator'] == '(':
            return "(" + to_mapcss(t['operands'][0]) + ")"
        elif t['operator'] == '!':
            return "!" + to_mapcss(t['operands'][0])
        elif not t['operator']:
            return to_mapcss(t['operands'][0])
        else:
            return to_mapcss(t['operands'][0]) + t['operator'] + to_mapcss(t['operands'][1])
    elif t['type'] == 'valueExpression':
        if t['operator'] == '(':
            return "(" + to_mapcss(t['operands'][0]) + ")"
        if not t['operator']:
            return to_mapcss(t['operands'][0])
        else:
            return to_mapcss(t['operands'][0]) + t['operator'] + to_mapcss(t['operands'][1])
    elif t['type'] == 'functionExpression':
        return t['name'] + "(" + ", ".join(map(to_mapcss, t['params'])) + ")"
    elif t['type'] == 'primaryExpression':
        return to_mapcss(t['value'])
    else:
        return "<UNKNOW TYPE {0}>".format(t['type'])


# This class defines a complete listener for a parse tree produced by MapCSSParser.
class MapCSSListenerL(MapCSSListener):
#    def __init__(self, lexer):
#        self.stylesheet = None

    # Enter a parse tree produced by MapCSSParser#stylesheet.
    def enterStylesheet(self, ctx:MapCSSParser.StylesheetContext):
        self.rules = []

    # Exit a parse tree produced by MapCSSParser#stylesheet.
    def exitStylesheet(self, ctx:MapCSSParser.StylesheetContext):
        self.stylesheet = {'type': 'stylesheet', 'rules': self.rules}


    # Enter a parse tree produced by MapCSSParser#rule_.
    def enterRule_(self, ctx:MapCSSParser.Rule_Context):
        self.selectors = []
        self.declarations = []

    # Exit a parse tree produced by MapCSSParser#rule_.
    def exitRule_(self, ctx:MapCSSParser.Rule_Context):
        self.rules.append({'type': 'rule', 'selectors': self.selectors, 'declarations': self.declarations})


    # Enter a parse tree produced by MapCSSParser#selector.
    def enterSelector(self, ctx:MapCSSParser.SelectorContext):
        self.simple_selectors = []
        self.link_selectors = []
        self.pseudo_class = []

    # Exit a parse tree produced by MapCSSParser#selector.
    def exitSelector(self, ctx:MapCSSParser.SelectorContext):
        self.selectors.append({'type': 'selector', 'simple_selectors': self.simple_selectors,
            'operator': (ctx.simple_selector_operator() and ctx.simple_selector_operator().getText()) or (ctx.OP_GT() and ctx.OP_GT().getText()),
            'link_selectors': self.link_selectors,
            'pseudo_class': self.pseudo_class})


    # Enter a parse tree produced by MapCSSParser#link_selector.
    def enterLink_selector(self, ctx:MapCSSParser.Link_selectorContext):
        self.stack = [{
            'valueExpressions': []
        }]

    # Exit a parse tree produced by MapCSSParser#link_selector.
    def exitLink_selector(self, ctx:MapCSSParser.Link_selectorContext):
        v = self.stack.pop()
        self.link_selectors.append({'type': 'link_selector',
            'operator': (ctx.valueOperator() or ctx.numericOperator()).getText(),
            'role': len(v['valueExpressions']) > 0 and v['valueExpressions'][0],
            'index': ctx.int_() and ctx.int_().getText()})


    # Enter a parse tree produced by MapCSSParser#simple_selector.
    def enterSimple_selector(self, ctx:MapCSSParser.Simple_selectorContext):
        self.class_selectors = []
        self.predicates = []
        self.predicates_function_base = None
        self.pseudo_class = []

    # Exit a parse tree produced by MapCSSParser#simple_selector.
    def exitSimple_selector(self, ctx:MapCSSParser.Simple_selectorContext):
        self.simple_selectors.append({'type': 'simple_selector',
            'type_selector': ctx.type_selector().getText(),
            'class_selectors': self.class_selectors,
            'predicates': self.predicates,
            'pseudo_class': self.pseudo_class})


    # Enter a parse tree produced by MapCSSParser#predicate.
    def enterPredicate(self, ctx:MapCSSParser.PredicateContext):
        self.stack = [{
            'predicate_simple': None,
            'booleanExpressions': []
        }]

    # Exit a parse tree produced by MapCSSParser#predicate.
    def exitPredicate(self, ctx:MapCSSParser.PredicateContext):
        predicate = self.stack.pop()
        self.predicates.append(predicate['predicate_simple'] or predicate['booleanExpressions'][0])


#    # Enter a parse tree produced by MapCSSParser#predicate_simple.
#    def enterPredicate_simple(self, ctx:MapCSSParser.Predicate_simpleContext):
#        pass

    # Exit a parse tree produced by MapCSSParser#predicate_simple.
    def exitPredicate_simple(self, ctx:MapCSSParser.Predicate_simpleContext):
        self.stack[-1]['predicate_simple'] = {'type': 'predicate_simple',
            'predicate': (ctx.predicate_ident() or ctx.quoted() or ctx.regexExpression()).getText(),
            'not': not(not(ctx.OP_NOT())),
            'question_mark': not(not(ctx.QUESTION_MARK()))}


#    # Enter a parse tree produced by MapCSSParser#class_selector.
#    def enterClass_selector(self, ctx:MapCSSParser.Class_selectorContext):
#        pass

    # Exit a parse tree produced by MapCSSParser#class_selector.
    def exitClass_selector(self, ctx:MapCSSParser.Class_selectorContext):
        self.class_selectors.append({'type': 'class_selector', 'not': not(not(ctx.OP_NOT())), 'class': ctx.cssident().getText()})


#    # Enter a parse tree produced by MapCSSParser#pseudo_class_selector.
#    def enterPseudo_class_selector(self, ctx:MapCSSParser.Pseudo_class_selectorContext):
#        pass

    # Exit a parse tree produced by MapCSSParser#pseudo_class_selector.
    def exitPseudo_class_selector(self, ctx:MapCSSParser.Pseudo_class_selectorContext):
        self.pseudo_class.append({'type': 'pseudo_class', 'not_class': not(not(ctx.OP_NOT())), 'pseudo_class': ctx.cssident().getText()})


    # Enter a parse tree produced by MapCSSParser#declaration.
    def enterDeclaration(self, ctx:MapCSSParser.DeclarationContext):
        self.params_stack = []
        self.params = []

        self.value = None

    # Exit a parse tree produced by MapCSSParser#declaration.
    def exitDeclaration(self, ctx:MapCSSParser.DeclarationContext):
        if len(self.params) > 0: # Case of declaration_value_function
            self.value = self.params[0]

        self.declarations.append({'type': 'declaration',
            'set': ctx.cssident() and ctx.cssident().getText(),
            'property': ctx.declaration_property() and ctx.declaration_property().getText(),
            'value': self.value})


#    # Enter a parse tree produced by MapCSSParser#declaration_value_single.
#    def enterDeclaration_value_single(self, ctx:MapCSSParser.Declaration_value_singleContext):
#        pass

    # Exit a parse tree produced by MapCSSParser#declaration_value_single.
    def exitDeclaration_value_single(self, ctx:MapCSSParser.Declaration_value_singleContext):
        self.params.append({'type': 'declaration_value_single', 'value': ctx.single_value().getText()})


    # Enter a parse tree produced by MapCSSParser#declaration_value_function.
    def enterDeclaration_value_function(self, ctx:MapCSSParser.Declaration_value_functionContext):
        self.params_stack.append(self.params)
        self.params = []

    # Exit a parse tree produced by MapCSSParser#declaration_value_function.
    def exitDeclaration_value_function(self, ctx:MapCSSParser.Declaration_value_functionContext):
        params = self.params
        self.params = self.params_stack.pop()
        self.params.append({'type': 'declaration_value_function',
            'name': ctx.cssident().getText(),
            'params': params})


    # Enter a parse tree produced by MapCSSParser#booleanExpression.
    def enterBooleanExpression(self, ctx:MapCSSParser.BooleanExpressionContext):
        self.stack.append({
            'booleanExpressions': [],
            'valueExpressions': [],
            'functionExpression': None
        })

    # Exit a parse tree produced by MapCSSParser#booleanExpression.
    def exitBooleanExpression(self, ctx:MapCSSParser.BooleanExpressionContext):
        v = self.stack.pop()
        self.stack[-1]['booleanExpressions'].append({
            'type': 'booleanExpression',
            'operator': None if v['functionExpression'] else
                (ctx.op and ctx.op.text) or
                (ctx.booleanOperator() or ctx.valueOperator() or ctx.regexOperator()).getText(),
            'operands': v['booleanExpressions'] + v['valueExpressions'] + (
                (ctx.regexExpression() and [ctx.regexExpression().getText()]) or 
                [v['functionExpression']] or
                []
            )
        })


    # Enter a parse tree produced by MapCSSParser#valueExpression.
    def enterValueExpression(self, ctx:MapCSSParser.ValueExpressionContext):
        self.stack.append({
            'valueExpressions': [],
            'primaryExpression': None,
            'functionExpression': None
        })

    # Exit a parse tree produced by MapCSSParser#valueExpression.
    def exitValueExpression(self, ctx:MapCSSParser.ValueExpressionContext):
        v = self.stack.pop()
        self.stack[-1]['valueExpressions'].append({
            'type': 'valueExpression',
            'operator': ctx.op and ctx.op.text,
            'operands': (len(v['valueExpressions']) > 0 and v['valueExpressions']) or [v['primaryExpression'] or v['functionExpression']]
        })


    # Enter a parse tree produced by MapCSSParser#functionExpression.
    def enterFunctionExpression(self, ctx:MapCSSParser.FunctionExpressionContext):
        self.stack.append({
            'valueExpressions': []
        })

    # Exit a parse tree produced by MapCSSParser#functionExpression.
    def exitFunctionExpression(self, ctx:MapCSSParser.FunctionExpressionContext):
        v = self.stack.pop()
        self.stack[-1]['functionExpression'] = {
            'type': 'functionExpression',
            'name': ctx.cssident().getText(),
            'params': v['valueExpressions']
        }


#    # Enter a parse tree produced by MapCSSParser#primaryExpression.
#    def enterPrimaryExpression(self, ctx:MapCSSParser.PrimaryExpressionContext):
#        pass

    # Exit a parse tree produced by MapCSSParser#primaryExpression.
    def exitPrimaryExpression(self, ctx:MapCSSParser.PrimaryExpressionContext):
        self.stack[-1]['primaryExpression'] = {
            'type': 'primaryExpression',
            'value': ctx.getText()
        }
