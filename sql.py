# An imperfect parser for SQL WHERE expressions.


# Python std
import re
import copy
import pprint


#whereExpr = r"(a = 'b' AND Games.Name REGEXP 'a.i' AND Developers.Developer LIKE '%know%' ESCAPE '\') OR (Games.Name LIKE '%n''s%' ESCAPE '\' AND Publishers.Publisher LIKE '%ny%' ESCAPE '\') OR rrr=sss"
#whereExpr = r"(Year >= 1986)"
#whereExpr = r"a AND b OR c AND d"
#whereExpr = r"(a OR b) AND c AND d"
#whereExpr = r"(Years.Year BETWEEN 1983 AND 1985)"

# + Tokenize {{{

def tokenizeWhereExpr(i_text):
    """
    Params:
     i_text:
      (str)

    Returns:
     (list)
     Each element is:
      (tuple)
      Tuple has elements:
       0:
        (str)
        Type of token
        One of
         "integer"
         "float"
         "keyword"
         "operator"
         "identifier"
         "("
         ")"
         "string"
       1:
        (str)
        The characters of the token.
    """
    i_text += " "

    tokens = []
    textPos = 0
    while textPos < len(i_text):
        match = re.match(r"\s+", i_text[textPos:])
        if match:
            textPos += match.end(0)
            continue

        match = re.match(r"([0-9]+\.[0-9]+|[0-9]+\.|\.[0-9]+)", i_text[textPos:], re.IGNORECASE)
        if match:
            tokens.append(("float", match.group(1)))
            textPos += match.end(1)
            continue

        match = re.match(r"([0-9]+)[^A-Z0-9_]", i_text[textPos:], re.IGNORECASE)
        if match:
            tokens.append(("integer", match.group(1)))
            textPos += match.end(1)
            continue

        match = re.match(r"(NULL)[^A-Z0-9_]", i_text[textPos:], re.IGNORECASE)
        if match:
            tokens.append(("keyword", match.group(1)))
            textPos += match.end(1)
            continue

        match = re.match(r"(AND|OR)[^A-Z0-9_]", i_text[textPos:], re.IGNORECASE)
        if match:
            tokens.append(("operator", match.group(1)))
            textPos += match.end(1)
            continue

        match = re.match(r"(REGEXP|LIKE|IS NOT|IS|ESCAPE|BETWEEN)[^A-Z0-9_]", i_text[textPos:], re.IGNORECASE)
        if match:
            tokens.append(("operator", match.group(1)))
            textPos += match.end(1)
            continue

        #match = re.match(r"(<=|>=|<|>|==|=|!=|<>|~)[^<>=!~]", i_text[textPos:])
        match = re.match(r"(<=|>=|<|>|==|=|!=|<>|~)", i_text[textPos:])
        if match:
            tokens.append(("operator", match.group(1)))
            textPos += match.end(1)
            continue

        #match = re.match(r"([A-Z0-9_]+.[A-Z0-9_]+|[A-Z0-9_]+)[^A-Z0-9_.]", i_text[textPos:], re.IGNORECASE)
        match = re.match(r"([A-Z0-9_]+\.[A-Z0-9_]+|[A-Z0-9_]+)", i_text[textPos:], re.IGNORECASE)
        if match:
            tokens.append(("identifier", match.group(1)))
            textPos += match.end(1)
            continue

        #match = re.match(r"([A-Z0-9_]+)[^A-Z0-9_]", i_text[textPos:], re.IGNORECASE)
        match = re.match(r"([A-Z0-9_]+)", i_text[textPos:], re.IGNORECASE)
        if match:
            tokens.append(("identifier", match.group(1)))
            textPos += match.end(1)
            continue

        match = re.match(r"\(", i_text[textPos:])
        if match:
            tokens.append(("(", match.group(0)))
            textPos += match.end(0)
            continue

        match = re.match(r"\)", i_text[textPos:])
        if match:
            tokens.append((")", match.group(0)))
            textPos += match.end(0)
            continue

        if i_text[textPos] == "'":
            endPos = textPos + 1
            while endPos < len(i_text):
                # If found a quote
                if i_text[endPos] == "'":
                    # If there's another one after it,
                    # it's a escaped quote so skip them both
                    if endPos + 1 < len(i_text) and i_text[endPos + 1] == "'":
                        endPos += 2
                    # Else if there isn't another one after it,
                    # it's a closing quote
                    else:
                        break
                else:
                    endPos += 1
            if i_text[endPos] != "'":
                return "Couldn't find end of string at pos: " + str(endPos)
            tokens.append(("string", i_text[textPos + 1:endPos].replace("''", "'")))
            textPos = endPos + 1
            continue

        return "No recognized word at pos: " + str(textPos)

    return tokens

#tokenized = tokenizeWhereExpr(whereExpr)

# + }}}

# + Parse {{{

def parseOperatorBetween_onStart(i_tokens):
    operators["AND"]["precedence"] += 3
def parseOperatorBetween_onEnd(i_tokens):
    operators["AND"]["precedence"] -= 3

initialOperators = {
    "ESCAPE": { "precedence": 6, "operands": 2 },
    "<=": { "precedence": 5, "operands": 2 },
    ">=": { "precedence": 5, "operands": 2 },
    "<": { "precedence": 5, "operands": 2 },
    ">": { "precedence": 5, "operands": 2 },
    "==": { "precedence": 5, "operands": 2 },
    "=": { "precedence": 5, "operands": 2 },
    "!=": { "precedence": 5, "operands": 2 },
    "<>": { "precedence": 5, "operands": 2 },
    "~": { "precedence": 5, "operands": 2 },
    "BETWEEN": { "precedence": 5, "operands": 2, "onStart": parseOperatorBetween_onStart, "onEnd": parseOperatorBetween_onEnd },
    "REGEXP": { "precedence": 5, "operands": 2 },
    "LIKE": { "precedence": 5, "operands": 2 },
    "IS": { "precedence": 5, "operands": 2 },
    "IS NOT": { "precedence": 5, "operands": 2 },
    "AND": { "precedence": 3, "operands": 2 },
    "OR": { "precedence": 2, "operands": 2 },
}

def initializeOperatorTable():
    global operators
    operators = copy.deepcopy(initialOperators)

def parseExpression(i_tokens):
    """
    Params:
     i_tokens:
      (list)

    Returns:
     Either (dict)
      Root node of syntax tree
     or (str)
      Description of error.
    """
    lhs = parseValue(i_tokens)
    return parseOperations(lhs, i_tokens, 0)

def parseValue(i_tokens):
    value = i_tokens.pop(0)
    if value[0] == "operator":
        raise RuntimeError("unexpected operator")
    elif value[0] == "(":
        # Parse subexpression
        subParse = parseExpression(i_tokens)
        # Validate presence of closing parenthesis
        # and skip over it
        if not (len(i_tokens) > 0 and i_tokens[0][0] == ")"):
            return "unclosed parenthesis"
        i_tokens.pop(0)
        return subParse
    else:
        return value

def parseOperations(i_lhs, i_tokens, i_precedingPrecedence):
    # If no more tokens
    # or if next operator is of equal precedence or a step down from what caller had,
    # return to caller so they can bind
    while len(i_tokens) > 0:
        op1 = i_tokens[0]
        if op1[0] != "operator":# and op1[0] != "conjunction":
            # syntax error
            break
        op1Precedence = operators[op1[1]]["precedence"]
        if op1Precedence <= i_precedingPrecedence:
            break

        #
        if "onStart" in operators[op1[1]]:
            operators[op1[1]]["onStart"](i_tokens)

        # Else if next operator is of higher precedence than what caller had,
        # get it and next value and recurse
        i_tokens.pop(0)
        rhs = parseValue(i_tokens)
        rhs = parseOperations(rhs, i_tokens, op1Precedence)

        #
        if "onEnd" in operators[op1[1]]:
            operators[op1[1]]["onEnd"](i_tokens)

        # Bind
        i_lhs = { "op": op1,
                  "children": [i_lhs, rhs] }

    return i_lhs

# + }}}

# + Postprocess {{{

def flattenOperator(i_node, i_operatorName):
    """
    Params:
     i_node:
      (dict)
      As returned from parseExpression()
     i_operatorName:
      (str)
      eg.
       "AND"
       "OR"
    """
    if type(i_node) != dict:
        return i_node

    flattenedChildren = [flattenOperator(child, i_operatorName)  for child in i_node["children"]]
    if i_node["op"][1].upper() != i_operatorName.upper():
        return { "op": i_node["op"],
                 "children": flattenedChildren }

    newOperands = []
    for flattenedChild in flattenedChildren:
        if type(flattenedChild) != dict:
            newOperands.append(flattenedChild)
        elif flattenedChild["op"][1].upper() != i_operatorName.upper():
            newOperands.append(flattenedChild)
        else:
            newOperands.extend(flattenedChild["children"])
    return { "op": i_node["op"],
             "children": newOperands }
        

#parsed = parseExpression(tokenized)
#import pdb
#pdb.run("parseExpression(tokenized)")

#flattened1 = flattenOperator(parsed, "AND")
#flattened1 = flattenOperator(flattened1, "OR")

#flattened2 = flattenOperator(parsed, "OR")
#flattened2 = flattenOperator(flattened2, "AND")

# + }}}
