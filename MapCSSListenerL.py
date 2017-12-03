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
            return to_mapcss(t['simple_selectors'][0]) + " " + t['operator'] + "".join(map(to_mapcss, t['link_selectors'])) + " " + to_mapcss(t['simple_selectors'][1])
        else:
            return "".join(map(to_mapcss, t['simple_selectors']))
    elif t['type'] == 'link_selector':
        if t['role']:
            return "[" + to_mapcss(t['role']) + "]"
        else: # t['index']
            return "[index=" + str(t['index']) + "]"
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
    elif t['type'] == 'predicate_operator':
        return to_mapcss(t['predicates'][0]) + t['op'] + to_mapcss(t['predicates'][1])
    elif t['type'] == 'predicate_function':
        return t['name'] + "(" + ", ".join(map(to_mapcss, t['params'])) + ")"
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

    # Exit a parse tree produced by MapCSSParser#selector.
    def exitSelector(self, ctx:MapCSSParser.SelectorContext):
        self.selectors.append({'type': 'selector', 'simple_selectors': self.simple_selectors,
            'operator': (ctx.simple_selector_operator() and ctx.simple_selector_operator().getText()) or (ctx.OP_GT() and ctx.OP_GT().getText()),
            'link_selectors': self.link_selectors})


    # Enter a parse tree produced by MapCSSParser#link_selector.
    def enterLink_selector(self, ctx:MapCSSParser.Link_selectorContext):
        self.predicate_primitive = None

    # Exit a parse tree produced by MapCSSParser#link_selector.
    def exitLink_selector(self, ctx:MapCSSParser.Link_selectorContext):
        self.link_selectors.append({'type': 'link_selector',
            'role': self.predicate_primitive,
            'index': ctx.int_() and ctx.int_().getText()})


    # Enter a parse tree produced by MapCSSParser#layer_id_selector.
    def enterLayer_id_selector(self, ctx:MapCSSParser.Layer_id_selectorContext):
        pass

    # Exit a parse tree produced by MapCSSParser#layer_id_selector.
    def exitLayer_id_selector(self, ctx:MapCSSParser.Layer_id_selectorContext):
        pass


    # Enter a parse tree produced by MapCSSParser#int_operator.
    def enterInt_operator(self, ctx:MapCSSParser.Int_operatorContext):
        pass

    # Exit a parse tree produced by MapCSSParser#int_operator.
    def exitInt_operator(self, ctx:MapCSSParser.Int_operatorContext):
        pass


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


#    # Enter a parse tree produced by MapCSSParser#quoted.
#    def enterQuoted(self, ctx:MapCSSParser.QuotedContext):
#        pass

#    # Exit a parse tree produced by MapCSSParser#quoted.
#    def exitQuoted(self, ctx:MapCSSParser.QuotedContext):
#        pass


#    # Enter a parse tree produced by MapCSSParser#cssident.
#    def enterCssident(self, ctx:MapCSSParser.CssidentContext):
#        pass

#    # Exit a parse tree produced by MapCSSParser#cssident.
#    def exitCssident(self, ctx:MapCSSParser.CssidentContext):
#        pass


#    # Enter a parse tree produced by MapCSSParser#attribute_selector.
#    def enterAttribute_selector(self, ctx:MapCSSParser.Attribute_selectorContext):
#        pass

#    # Exit a parse tree produced by MapCSSParser#attribute_selector.
#    def exitAttribute_selector(self, ctx:MapCSSParser.Attribute_selectorContext):
#        pass


    # Enter a parse tree produced by MapCSSParser#predicate.
    def enterPredicate(self, ctx:MapCSSParser.PredicateContext):
        self.stack = [{
            'predicate_simple': None,
            'predicate_operator': None,
            'predicate_functions': []
        }]

    # Exit a parse tree produced by MapCSSParser#predicate.
    def exitPredicate(self, ctx:MapCSSParser.PredicateContext):
        predicate = self.stack.pop()
        self.predicates.append(predicate['predicate_simple'] or predicate['predicate_operator'] or predicate['predicate_functions'][0])


#    # Enter a parse tree produced by MapCSSParser#predicate_simple.
#    def enterPredicate_simple(self, ctx:MapCSSParser.Predicate_simpleContext):
#        pass

    # Exit a parse tree produced by MapCSSParser#predicate_simple.
    def exitPredicate_simple(self, ctx:MapCSSParser.Predicate_simpleContext):
        self.stack[-1]['predicate_simple'] = {'type': 'predicate_simple',
            'predicate': (ctx.predicate_ident() or ctx.quoted()).getText(),
            'not': not(not(ctx.OP_NOT())),
            'question_mark': not(not(ctx.QUESTION_MARK()))}


    # Enter a parse tree produced by MapCSSParser#predicate_operator.
    def enterPredicate_operator(self, ctx:MapCSSParser.Predicate_operatorContext):
        self.stack.append({
            'predicate_primitives': []
        })

    # Exit a parse tree produced by MapCSSParser#predicate_operator.
    def exitPredicate_operator(self, ctx:MapCSSParser.Predicate_operatorContext):
        predicate_primitives = self.stack.pop()['predicate_primitives']
        self.stack[-1]['predicate_operator'] = {'type': 'predicate_operator',
            'predicates': [predicate_primitives[0], len(predicate_primitives) >=2 and predicate_primitives[1] or ctx.rhs_match().getText()],
            'op': (ctx.binary_operator() and ctx.binary_operator().getText()) or
                (ctx.OP_MATCH() and ctx.OP_MATCH().getText()) or
                (ctx.OP_NOT_MATCH() and ctx.OP_NOT_MATCH().getText())}


    # Enter a parse tree produced by MapCSSParser#predicate_function.
    def enterPredicate_function(self, ctx:MapCSSParser.Predicate_functionContext):
        self.stack.append({
            'predicate_function_param': []
        })

    # Exit a parse tree produced by MapCSSParser#predicate_function.
    def exitPredicate_function(self, ctx:MapCSSParser.Predicate_functionContext):
        params = self.stack.pop()['predicate_function_param']
        self.stack[-1]['predicate_functions'].append({'type': 'predicate_function',
            'name': ctx.cssident() and ctx.cssident().getText(),
            'params': params})


    # Enter a parse tree produced by MapCSSParser#predicate_function_param.
    def enterPredicate_function_param(self, ctx:MapCSSParser.Predicate_function_paramContext):
        self.stack.append({
            'predicate_functions': []
        })

    # Exit a parse tree produced by MapCSSParser#predicate_function_param.
    def exitPredicate_function_param(self, ctx:MapCSSParser.Predicate_function_paramContext):
        predicate_function = self.stack.pop()['predicate_functions']
        self.stack[-1]['predicate_function_param'].append(ctx.single_value() and ctx.single_value().getText() or predicate_function[0])


#    # Enter a parse tree produced by MapCSSParser#predicate_ident.
#    def enterPredicate_ident(self, ctx:MapCSSParser.Predicate_identContext):
#        pass

#    # Exit a parse tree produced by MapCSSParser#predicate_ident.
#    def exitPredicate_ident(self, ctx:MapCSSParser.Predicate_identContext):
#        pass


    # Enter a parse tree produced by MapCSSParser#predicate_primitive.
    def enterPredicate_primitive(self, ctx:MapCSSParser.Predicate_primitiveContext):
        self.stack.append({
            'predicate_functions': []
        })

    # Exit a parse tree produced by MapCSSParser#predicate_primitive.
    def exitPredicate_primitive(self, ctx:MapCSSParser.Predicate_primitiveContext):
        predicate_function = self.stack.pop()['predicate_functions']
        self.stack[-1]['predicate_primitives'].append((ctx.single_value() and ctx.single_value().getText()) or (ctx.predicate_ident() and ctx.predicate_ident().getText()) or predicate_function[0])


    # Enter a parse tree produced by MapCSSParser#rhs_match.
    def enterRhs_match(self, ctx:MapCSSParser.Rhs_matchContext):
        pass

    # Exit a parse tree produced by MapCSSParser#rhs_match.
    def exitRhs_match(self, ctx:MapCSSParser.Rhs_matchContext):
        pass


    # Enter a parse tree produced by MapCSSParser#binary_operator.
    def enterBinary_operator(self, ctx:MapCSSParser.Binary_operatorContext):
        pass

    # Exit a parse tree produced by MapCSSParser#binary_operator.
    def exitBinary_operator(self, ctx:MapCSSParser.Binary_operatorContext):
        pass


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


#    # Enter a parse tree produced by MapCSSParser#type_selector.
#    def enterType_selector(self, ctx:MapCSSParser.Type_selectorContext):
#        pass

#    # Exit a parse tree produced by MapCSSParser#type_selector.
#    def exitType_selector(self, ctx:MapCSSParser.Type_selectorContext):
#        pass


#    # Enter a parse tree produced by MapCSSParser#declaration_block.
#    def enterDeclaration_block(self, ctx:MapCSSParser.Declaration_blockContext):
#        pass

#    # Exit a parse tree produced by MapCSSParser#declaration_block.
#    def exitDeclaration_block(self, ctx:MapCSSParser.Declaration_blockContext):
#        pass


#    # Enter a parse tree produced by MapCSSParser#declarations.
#    def enterDeclarations(self, ctx:MapCSSParser.DeclarationsContext):
#        pass

#    # Exit a parse tree produced by MapCSSParser#declarations.
#    def exitDeclarations(self, ctx:MapCSSParser.DeclarationsContext):
#        pass


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


#    # Enter a parse tree produced by MapCSSParser#declaration_property.
#    def enterDeclaration_property(self, ctx:MapCSSParser.Declaration_propertyContext):
#        pass

#    # Exit a parse tree produced by MapCSSParser#declaration_property.
#    def exitDeclaration_property(self, ctx:MapCSSParser.Declaration_propertyContext):
#        pass


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


#    # Enter a parse tree produced by MapCSSParser#num.
#    def enterNum(self, ctx:MapCSSParser.NumContext):
#        pass

#    # Exit a parse tree produced by MapCSSParser#num.
#    def exitNum(self, ctx:MapCSSParser.NumContext):
#        pass


#    # Enter a parse tree produced by MapCSSParser#single_value.
#    def enterSingle_value(self, ctx:MapCSSParser.Single_valueContext):
#        pass

#    # Exit a parse tree produced by MapCSSParser#single_value.
#    def exitSingle_value(self, ctx:MapCSSParser.Single_valueContext):
#        pass


    # Enter a parse tree produced by MapCSSParser#expr.
    def enterExpr(self, ctx:MapCSSParser.ExprContext):
        pass

    # Exit a parse tree produced by MapCSSParser#expr.
    def exitExpr(self, ctx:MapCSSParser.ExprContext):
        pass


    # Enter a parse tree produced by MapCSSParser#args.
    def enterArgs(self, ctx:MapCSSParser.ArgsContext):
        pass

    # Exit a parse tree produced by MapCSSParser#args.
    def exitArgs(self, ctx:MapCSSParser.ArgsContext):
        pass


    # Enter a parse tree produced by MapCSSParser#logicalExpression.
    def enterLogicalExpression(self, ctx:MapCSSParser.LogicalExpressionContext):
        pass

    # Exit a parse tree produced by MapCSSParser#logicalExpression.
    def exitLogicalExpression(self, ctx:MapCSSParser.LogicalExpressionContext):
        pass


    # Enter a parse tree produced by MapCSSParser#booleanAndExpression.
    def enterBooleanAndExpression(self, ctx:MapCSSParser.BooleanAndExpressionContext):
        pass

    # Exit a parse tree produced by MapCSSParser#booleanAndExpression.
    def exitBooleanAndExpression(self, ctx:MapCSSParser.BooleanAndExpressionContext):
        pass


    # Enter a parse tree produced by MapCSSParser#equalityExpression.
    def enterEqualityExpression(self, ctx:MapCSSParser.EqualityExpressionContext):
        pass

    # Exit a parse tree produced by MapCSSParser#equalityExpression.
    def exitEqualityExpression(self, ctx:MapCSSParser.EqualityExpressionContext):
        pass


    # Enter a parse tree produced by MapCSSParser#relationalExpression.
    def enterRelationalExpression(self, ctx:MapCSSParser.RelationalExpressionContext):
        pass

    # Exit a parse tree produced by MapCSSParser#relationalExpression.
    def exitRelationalExpression(self, ctx:MapCSSParser.RelationalExpressionContext):
        pass


    # Enter a parse tree produced by MapCSSParser#additiveExpression.
    def enterAdditiveExpression(self, ctx:MapCSSParser.AdditiveExpressionContext):
        pass

    # Exit a parse tree produced by MapCSSParser#additiveExpression.
    def exitAdditiveExpression(self, ctx:MapCSSParser.AdditiveExpressionContext):
        pass


    # Enter a parse tree produced by MapCSSParser#multiplicativeExpression.
    def enterMultiplicativeExpression(self, ctx:MapCSSParser.MultiplicativeExpressionContext):
        pass

    # Exit a parse tree produced by MapCSSParser#multiplicativeExpression.
    def exitMultiplicativeExpression(self, ctx:MapCSSParser.MultiplicativeExpressionContext):
        pass


    # Enter a parse tree produced by MapCSSParser#unaryExpression.
    def enterUnaryExpression(self, ctx:MapCSSParser.UnaryExpressionContext):
        pass

    # Exit a parse tree produced by MapCSSParser#unaryExpression.
    def exitUnaryExpression(self, ctx:MapCSSParser.UnaryExpressionContext):
        pass


    # Enter a parse tree produced by MapCSSParser#primaryExpression.
    def enterPrimaryExpression(self, ctx:MapCSSParser.PrimaryExpressionContext):
        pass

    # Exit a parse tree produced by MapCSSParser#primaryExpression.
    def exitPrimaryExpression(self, ctx:MapCSSParser.PrimaryExpressionContext):
        pass
