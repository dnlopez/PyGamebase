# An imperfect parser for SQL WHERE expressions.


# Python std
import re
import copy
import pprint


#whereExpr = r"(a = 'b' AND Games.Name REGEXP 'a.i' AND Developers.Developer LIKE '%know%' ESCAPE '\') OR (Games.Name LIKE '%n''s%' ESCAPE '\' AND Publishers.Publisher LIKE '%ny%' ESCAPE '\') OR rrr=sss"
#whereExpr = "(a = 'b' AND [Games.Name] REGEXP 'a.i' AND [Developers].[Developer] LIKE '%know%' ESCAPE '\') OR (\"Games.Name\" LIKE '%n''s%' ESCAPE '\' AND `Publishers`.\"Publisher\" LIKE '%ny%' ESCAPE '\') OR rrr=sss"
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
         "."
         "("
         ")"
         "string"
       1:
        (str)
        The characters of the token.
       2:
        (int)
        The start position of the token in i_text.
       3:
        (int)
        The (non-inclusive) end position of the token in i_text.
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
            tokens.append(("float", match.group(1), textPos, textPos + match.end(1)))
            textPos += match.end(1)
            continue

        match = re.match(r"([0-9]+)[^A-Z0-9_]", i_text[textPos:], re.IGNORECASE)
        if match:
            tokens.append(("integer", match.group(1), textPos, textPos + match.end(1)))
            textPos += match.end(1)
            continue

        match = re.match(r"(NULL)[^A-Z0-9_]", i_text[textPos:], re.IGNORECASE)
        if match:
            tokens.append(("keyword", match.group(1), textPos, textPos + match.end(1)))
            textPos += match.end(1)
            continue

        match = re.match(r"(AND|OR)[^A-Z0-9_]", i_text[textPos:], re.IGNORECASE)
        if match:
            tokens.append(("operator", match.group(1), textPos, textPos + match.end(1)))
            textPos += match.end(1)
            continue

        match = re.match(r"(REGEXP|LIKE|IS NOT|IS|ESCAPE|BETWEEN)[^A-Z0-9_]", i_text[textPos:], re.IGNORECASE)
        if match:
            tokens.append(("operator", match.group(1), textPos, textPos + match.end(1)))
            textPos += match.end(1)
            continue

        #match = re.match(r"(<=|>=|<|>|==|=|!=|<>|~)[^<>=!~]", i_text[textPos:])
        match = re.match(r"(<=|>=|<|>|==|=|!=|<>|~)", i_text[textPos:])
        if match:
            tokens.append(("operator", match.group(1), textPos, textPos + match.end(1)))
            textPos += match.end(1)
            continue

        match = re.match(r'(".*?"|\[.*?\]|`.*?`|[A-Z0-9_]+)', i_text[textPos:], re.IGNORECASE)
        if match:
            tokens.append(("identifier", match.group(1), textPos, textPos + match.end(1)))
            textPos += match.end(1)
            continue

        match = re.match(r"\.", i_text[textPos:])
        if match:
            tokens.append((".", match.group(0), textPos, textPos + match.end(0)))
            textPos += match.end(0)
            continue

        match = re.match(r"\(", i_text[textPos:])
        if match:
            tokens.append(("(", match.group(0), textPos, textPos + match.end(0)))
            textPos += match.end(0)
            continue

        match = re.match(r"\)", i_text[textPos:])
        if match:
            tokens.append((")", match.group(0), textPos, textPos + match.end(0)))
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
            endPos += 1
            tokens.append(("string", i_text[textPos:endPos], textPos, endPos))
            textPos = endPos
            continue

        return "Unrecognized token at pos: " + str(textPos)

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

class AstNode():
    def __init__(self, i_token):
        """
        Params:
         i_token:
          (tuple)
        """
        self.token = i_token

class ValueNode(AstNode):
    def __init__(self, i_token, i_type, i_value):
        """
        Params:
         i_token:
          (tuple)
         i_type:
          (str)
          One of
           "integer"
           "float"
           "keyword"
           "identifier"
           "string"
         i_value:
          If i_type is "integer"
           (int)
          Else if i_type is "float"
           (float)
          Else if i_type is "keyword", "identifier" or "string"
           (str)
        """
        super().__init__(i_token)

        self.type = i_type
        self.value = i_value

    def __repr__(self):
        if self.type == "string":
            return "V:'" + self.value.replace("'", "''") + "'"
        else:
            return "V:" + str(self.value)

    def toSqlString(self):
        """
        Returns:
         (str)
        """
        if self.type == "string":
            return "'" + self.value.replace("'", "''") + "'"
        else:
            return str(self.value)

class OperatorNode(AstNode):
    def __init__(self, i_token):
        """
        Params:
         i_token:
          (tuple)
          A token (as produced by tokenizeWhereExpr()) which must be of the following types (as specified in the first element of the tuple):
           "operator"
        """
        super().__init__(i_token)

        self.operation = i_token[1].upper()
        self.operands = []

    def __repr__(self):
        return "" + self.operation + "(" + ", ".join([str(operand)  for operand in self.operands]) + ")"

    def toSqlString(self):
        """
        Returns:
         (str)
        """
        return "(" + (" " + self.operation + " ").join([operand.toSqlString()  for operand in self.operands]) + ")"

def parseExpression(i_tokens):
    """
    Params:
     i_tokens:
      (list)

    Returns:
     Either (AstNode)
      Root node of syntax tree
     or raise RuntimeError
      with value:
       (str)
       Description of error.
    """
    lhs = parseValue(i_tokens)
    return parseOperations(lhs, i_tokens, 0)

def unquoteString(i_str):
    """
    Params:
     i_str:
      (str)

    Returns:
     (str)
    """
    if not ((i_str.startswith("'") and i_str.endswith("'"))):
        return i_str

    return i_str[1:-1].replace("''", "'")

def unquoteIdentifier(i_str):
    """
    Params:
     i_str:
      (str)

    Returns:
     (str)
    """
    if not ((i_str.startswith('"') and i_str.endswith('"')) or \
            (i_str.startswith("[") and i_str.endswith("]")) or \
            (i_str.startswith("`") and i_str.endswith("`"))):
        return i_str

    return i_str[1:-1]

def parseValue(i_tokens):
    """
    Params:
     i_tokens:
      (list)

    Returns:
     Either (AstNode)
      Root node of syntax tree
     or raise RuntimeError
      with value:
       (str)
       Description of error.
    """
    token = i_tokens.pop(0)
    if token[0] == "operator":
        raise RuntimeError("unexpected operator")
    elif token[0] == ")":
        raise RuntimeError("unexpected close parenthesis")
    elif token[0] == "(":
        # Parse subexpression
        subParse = parseExpression(i_tokens)
        # Validate presence of closing parenthesis
        # and skip over it
        if not (len(i_tokens) > 0 and i_tokens[0][0] == ")"):
            raise RuntimeError("unclosed parenthesis")
        i_tokens.pop(0)
        return subParse
    elif token[0] == "integer":
        return ValueNode(token, "integer", int(token[1]))
    elif token[0] == "float":
        return ValueNode(token, "float", float(token[1]))
    elif token[0] == "keyword":
        return ValueNode(token, "keyword", token[1])
    elif token[0] == "identifier":
        valueNode = ValueNode(token, "identifier", unquoteIdentifier(token[1]))
        # TODO store parsed sub-identifiers as arrays
        while len(i_tokens) >= 2 and i_tokens[0][0] == "." and i_tokens[1][0] == "identifier":
            token = i_tokens.pop(0)
            token = i_tokens.pop(0)
            valueNode.value += "." + unquoteIdentifier(token[1])
        return valueNode
    elif token[0] == "string":
        return ValueNode(token, "string", unquoteString(token[1]))

def parseOperations(i_lhs, i_tokens, i_precedingPrecedence):
    # If no more tokens
    # or if next operator is of equal precedence or a step down from what caller had,
    # return to caller so they can bind
    while len(i_tokens) > 0:
        if i_tokens[0][0] != "operator":
            # syntax error
            break
        
        op1 = OperatorNode(i_tokens[0])
        op1Precedence = operators[op1.operation]["precedence"]
        if op1Precedence <= i_precedingPrecedence:
            break

        #
        if "onStart" in operators[op1.operation]:
            operators[op1.operation]["onStart"](i_tokens)

        # Else if next operator is of higher precedence than what caller had,
        # get it and next value and recurse
        i_tokens.pop(0)
        rhs = parseValue(i_tokens)
        rhs = parseOperations(rhs, i_tokens, op1Precedence)

        #
        if "onEnd" in operators[op1.operation]:
            operators[op1.operation]["onEnd"](i_tokens)

        # Bind
        op1.operands = [i_lhs, rhs]
        i_lhs = op1

    return i_lhs

# + }}}

# + Postprocess {{{

def flattenOperator(i_node, i_operatorName):
    """
    Params:
     i_node:
      (AstNode)
      As returned from parseExpression()
     i_operatorName:
      (str)
      eg.
       "AND"
       "OR"
    """
    # If this isn't an operator
    # then there's nothing to flatten
    if not isinstance(i_node, OperatorNode):
        return i_node

    # Recurse to flatten the children,
    # and then if this operator's operation isn't the one we're trying to flatten,
    # just return this node with those flattened children
    flattenedChildren = [flattenOperator(child, i_operatorName)  for child in i_node.operands]
    if i_node.operation != i_operatorName.upper():
        newNode = copy.copy(i_node)
        newNode.operands = flattenedChildren
        return newNode

    # Else if this operator's operation is the one we're trying to flatten,
    # for any child which is the same operator,
    # move their operands up into our own operand array
    newOperands = []
    for flattenedChild in flattenedChildren:
        if isinstance(flattenedChild, OperatorNode) and flattenedChild.operation == i_operatorName.upper():
            newOperands.extend(flattenedChild.operands)
        else:
            newOperands.append(flattenedChild)
    newNode = copy.copy(i_node)
    newNode.operands = newOperands
    return newNode

#initializeOperatorTable()
#parsed = parseExpression(tokenized)
#import pdb
#pdb.run("parseExpression(tokenized)")

#flattened1 = flattenOperator(parsed, "AND")
#flattened1 = flattenOperator(flattened1, "OR")

#flattened2 = flattenOperator(parsed, "OR")
#flattened2 = flattenOperator(flattened2, "AND")

# + }}}

# + Reinterpret results {{{

import columns

# + + For column filters {{{

def interpretColumnOperation(i_node):
    """
    Params:
     i_node:
      (AstNode)

    Returns:
     (tuple)
     Tuple has elements:
      Either
       0:
        (str)
        Operator name
        eg.
         "="
         "LIKE"
       1:
        (str)
        DB column identifier
        eg.
         "Games.Name"
         "Name"
       2:
        (str)
        Value
        eg.
         "Uridium"
         "Uri%"
      or
       (None, None, None)
    """
    if not isinstance(i_node, OperatorNode):
        return None, None, None
    operation = i_node.operation

    # Scan operands,
    # and attempt to pick out one and only one identifier token to be the column name,
    # and one and only one token of another type to be the value
    columnName = None
    value = None
    for child in i_node.operands:
        # If the operand is itself a child operator
        if isinstance(child, OperatorNode):
            # If it's an 'ESCAPE' operator (an adjunct to 'LIKE'),
            # pull the actual value (as opposed to the escape character) from out of it
            if child.operation == "ESCAPE":
                value = child.operands[0].value  # TODO unescape?
            # If it's an 'AND' operator beneath a 'BETWEEN',
            # assemble the two values with a tilde between them
            elif operation == "BETWEEN" and child.operation == "AND":
                value = child.operands[0].value + "~" + child.operands[1].value
            # If it's some other child operator,
            # don't know how to deal with this so far
            else:
                return None, None, None
        #
        else: # isinstance(child, ValueNode):
            # If it's an identifier,
            # consider it the column name,
            # but fail if we already have one
            if child.type == "identifier":
                if columnName != None:
                    return None, None, None
                columnName = child.value
            # Else if it's not an identifier,
            # consider it the value,
            # but fail if we already have one
            else:
                if value != None:
                    return None, None, None
                value = child.value

    if operation == None or columnName == None or value == None:
        return None, None, None
    return operation, columnName, value

def sqlWhereExpressionToColumnFilters(i_whereExpression, i_skipFailures=False):
    """
    Parse SQL WHERE expression
    and get it as an equivalent set of column names and texts to enter into those boxes on the column filter bar.

    Params:
     i_whereExpression:
      (str)
     i_skipFailures:
      (bool)

    Returns:
     Either (list)
      An element for each 'row' of filter edits in the UI.
      Each element is:
       (dict with arbitrary key-value properties)
       The filter UI text for a particular column.
       Dict has:
        Keys:
         (str)
         ID of column
        Value:
         (str)
         Text for the filter box.
     or (None)
      Failed to get SQL expression into the simple column filter bar-compatible form.
      Perhaps it is too complex for that UI, too complex for the simple SQL parser, etc.
    """
    # Tokenize, parse and postprocess WHERE expression
    tokenized = tokenizeWhereExpr(i_whereExpression)
    if len(tokenized) == 0:
        return []
    initializeOperatorTable()
    parsed = parseExpression(tokenized)
    #print(parsed)
    if parsed == None:
        label_statusbar.setText("Failed to parse")
        return None
    parsed = flattenOperator(parsed, "AND")
    parsed = flattenOperator(parsed, "OR")

    # Get or simulate a top-level OR array from the input parse tree
    if isinstance(parsed, OperatorNode) and parsed.operation == "OR":
        orExpressions = parsed.operands
    else:
        orExpressions = [parsed]

    # Initialize an output top-level OR array,
    # and then for every input OR expression
    oredRows = []
    for orExpressionNo, orExpression in enumerate(orExpressions):

        # Get or simulate a second-level AND array from the input parse tree
        if isinstance(orExpression, OperatorNode) and orExpression.operation == "AND":
            andExpressions = parsed.operands
        else:
            andExpressions = [orExpression]

        # Initialize an output second-level AND dict,
        # and then for every input AND expression
        andedFields = {}
        for andExpression in andExpressions:
            # Get important parts of term
            operator, columnName, value = interpretColumnOperation(andExpression)
            #print("operator, columnName, value: " + str((operator, columnName, value)))

            # If that failed,
            # either skip this term or fail the whole extraction
            # [though maybe we should just skip over this andExpression as it could be just a useless term like "1=1"]
            if operator == None and columnName == None and value == None:
                if i_skipFailures:
                    continue
                else:
                    label_statusbar.setText("Failed to interpret column")  # TODO
                    return None

            # If the column name actually corresponds to a database field
            tableColumnSpec = columns.tableColumnSpec_getByDbIdentifier(columnName)
            if tableColumnSpec != None:
                widgetText = None
                strValue = str(value)
                if operator == "LIKE":
                    # If have percent sign at beginning and end and nowhere else
                    if len(strValue) >= 2 and strValue[0] == "%" and strValue[-1] == "%" and strValue[1:-1].find("%") == -1:
                        widgetText = strValue[1:-1]
                    else:
                        widgetText = strValue
                elif operator == "REGEXP":
                    widgetText = "/" + strValue + "/"
                elif operator == "BETWEEN":
                    widgetText = strValue
                elif operator == "IS":
                    widgetText = "=" + strValue
                elif operator == "IS NOT":
                    widgetText = "<>" + strValue
                elif operator == "=" or operator == "==":
                    widgetText = "=" + strValue
                elif operator == "<":
                    widgetText = "<" + strValue
                elif operator == "<=":
                    widgetText = "<=" + strValue
                elif operator == ">":
                    widgetText = ">" + strValue
                elif operator == ">=":
                    widgetText = ">=" + strValue
                elif operator == "<>" or operator == "!=":
                    widgetText = "<>" + strValue

                # Save widget text in output dict
                if widgetText != None:
                    andedFields[tableColumnSpec["id"]] = widgetText

        #
        oredRows.append(andedFields)

    return oredRows

# + + }}}

# + + For freeform SQL filtering {{{

def sqlWhereExpressionToColumnIdentifiers(i_whereExpression):
    """
    Parse SQL WHERE expression
    and get parts of it that look like column names or expressions.

    Params:
     i_sqlWhereExpression:
      (str)

    Returns:
     (list of str)
    """
    # Tokenize and parse WHERE expression
    tokenized = tokenizeWhereExpr(i_whereExpression)
    if len(tokenized) == 0:
        return []
    initializeOperatorTable()
    parsed = parseExpression(tokenized)
    #print(parsed)
    if parsed == None:
        label_statusbar.setText("Failed to parse")
        return None

    # Collect and return column identifiers
    def collectColumnIdentifiers(i_node):
        """
        Returns:
         (list of str)
        """
        columnIdentifiers = []

        if isinstance(i_node, OperatorNode):
            for operand in i_node.operands:
                columnIdentifiers += collectColumnIdentifiers(operand)
        else: # isinstance(child, ValueNode):
            if i_node.type == "identifier":
                columnIdentifiers.append(i_node.value)

        return columnIdentifiers
    return collectColumnIdentifiers(parsed)

import db
def normalizeSqlWhereExpressionToTableNamesAndSelectTerms(i_whereExpression, i_schemaName):
    """
    Parse SQL WHERE expression
    and both get and normalize parts of it that look like column names or expressions.

    Params:
     i_whereExpression:
      (str)
     i_schemaName:
      (str)

    Returns:
     (tuple)
     Tuple has elements:
      Either
       0:
        (str)
        Normalized SQL WHERE expression
       1:
        (set)
        Table names
       2:
        (set)
        SQL SELECT terms
      or
       (None, None, None)
       i_whereExpression was empty, [...]
    """
    # Tokenize and parse WHERE expression
    tokenized = tokenizeWhereExpr(i_whereExpression)
    if len(tokenized) == 0:
        return None, None, None
    initializeOperatorTable()
    parsed = parseExpression(tokenized)
    #print(parsed)
    if parsed == None:
        label_statusbar.setText("Failed to parse")
        return None, None, None

    # Collect and return column identifiers
    def normalizeIdentifiersAndCollectTableNamesAndSelectTerms(i_schemaName, io_node):
        """
        Params:
         i_schemaName:
          (str)
         io_node:
          (dict)

        Returns:
         Function return value:
          (tuple)
          Tuple has elements:
           0:
            (set)
            Table names
           1:
            (set)
            SQL SELECT terms
         io_node:
          Identifier names may be modified
        """
        neededTableNames = set()
        neededSelectTerms = set()

        if isinstance(io_node, OperatorNode):
            for operand in io_node.operands:
                newNeededTableNames, newNeededSelectTerms = normalizeIdentifiersAndCollectTableNamesAndSelectTerms(i_schemaName, operand)
                neededTableNames |= newNeededTableNames
                neededSelectTerms |= newNeededSelectTerms
        else: # isinstance(child, ValueNode):
            if io_node.type == "identifier":
                # If recognize the column,
                # normalize the identifier, modifying the node
                tableColumnSpec = columns.tableColumnSpec_getByDbIdentifier(io_node.value)
                if tableColumnSpec != None:
                    # Normalize identifier name in the parsed SQL
                    io_node.value = '"' + tableColumnSpec["dbIdentifiers"][0] + '"'
                    # Collect needed FROM and SELECT terms
                    newNeededTableNames, newNeededSelectTerms = db.tableColumnSpecToTableNamesAndSelectTerms(tableColumnSpec, i_schemaName)
                    neededTableNames |= newNeededTableNames
                    neededSelectTerms |= newNeededSelectTerms

        return neededTableNames, neededSelectTerms

    neededTableNames, neededSelectTerms = normalizeIdentifiersAndCollectTableNamesAndSelectTerms(i_schemaName, parsed)
    return (parsed.toSqlString(), neededTableNames, neededSelectTerms)

# + + }}}

# + }}}
