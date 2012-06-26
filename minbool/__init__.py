#
# Implementation of Quine McCluskey algorithm for simplifying boolean
# expressions.
#
import ast
import codegen
import functools
import sys


def simplify(expr):
    """
    Parses and simplifies an arbitrary Python boolean expression string.  The
    `expr` string is parsed using Python's 'ast' module.  The return value is
    an instance of BooleanExpression.  Casting the return value to string will
    yield the simplified expression as a string.  Calling the 'ast' method on
    the return value will return the ast for the simplified expression.
    """
    expression = _ASTExpression(expr)
    return synthesize(expression, *expression.propositions)


def synthesize(f, *names):
    """
    Synthesizes a boolean expression from an arbitrary function.  The names
    passed to this function are the names of the arguments passed to the
    function.  The function must accept the same number of boolean arguments as
    the number of names supplied and the function must return a boolean.  The
    function may also return None to indicate that we don't care about the
    answer for a particular input.

    This function will construct a truth table by iterating over all possible
    inputs to the function and recording the function's output.  The truth table
    is then used to synthesize a matching, simplified boolean expression using
    the Quine-McCluskey algorithm.

    The return value is an instance of BooleanExpression.  Casting the return
    value to string will yield a Python format boolean expression as a string.
    Calling the return value with boolean arguments will return the boolean
    result of the expression.
    """
    N = len(names)

    # Construct truth table
    truthtable = {}
    for minterm in _range_minterms(N):
        truthtable[minterm] = f(*minterm)

    # Find prime implicants
    prime_implicants = set()

    # Construct the first column
    column = [[] for _ in xrange(N+1)]
    for minterm, truth in truthtable.items():
        if truth in (True, None):  # include don't cares
            group = 0
            for member in minterm:
                if member:
                    group += 1
            column[group].append(minterm)

    # Iteratively find matches/prime implicants in successive columns
    done = False
    while not done:
        done = True
        next_column  = [set() for _ in xrange(N+1)]
        matches = [[False for _ in xrange(len(column[n]))] for n in xrange(N+1)]
        for n in xrange(N):
            this_group = column[n]
            next_group = column[n+1]
            for i, implicant in enumerate(this_group):
                for j, candidate in enumerate(next_group):
                    match = _adjacent(implicant, candidate)
                    if match:
                        matches[n][i] = matches[n+1][j] = True
                        group = 0
                        for member in match:
                            if member:
                                group += 1
                        next_column[group].add(match)
                        done = False

        for i in xrange(N+1):
            for j in xrange(len(matches[i])):
                if not matches[i][j]:
                    prime_implicants.add(tuple(column[i][j]))

        column = [list(group) for group in next_column]

    # construct coverage chart
    minterm_coverage = {}
    implicant_coverage = dict(
        [(implicant, set()) for implicant in prime_implicants])
    uncovered_minterms = set()
    for minterm, truth in truthtable.items():
        if not truth:
            continue # Don't care about coverage for don't cares
        uncovered_minterms.add(minterm)
        minterm_coverage[minterm] = covering_implicants = []
        for implicant in prime_implicants:
            if _covers(implicant, minterm):
                covering_implicants.append(implicant)
                implicant_coverage[implicant].add(minterm)

    # find essential implicants
    cand_implicants = set(prime_implicants)
    solution = []
    for minterm, covering_implicants in minterm_coverage.items():
        if minterm not in uncovered_minterms:
            # Might have gotten covered by an essential implicant found earlier
            continue

        if len(covering_implicants) == 1:
            # covering implicant is essential
            implicant = covering_implicants[0]
            solution.append(implicant)
            cand_implicants.remove(implicant)
            covered_minterms = implicant_coverage[implicant]
            uncovered_minterms -= covered_minterms

    # Add enough non-essential implicants to cover the remaining uncovered
    # minterms
    while uncovered_minterms:
        max_covered = 0
        leading_implicant = None
        for implicant in cand_implicants:
            covered_minterms = implicant_coverage[implicant]
            covered = 0
            for minterm in covered_minterms:
                if minterm in uncovered_minterms:
                    covered += 1

            if covered > max_covered:
                max_covered = covered
                leading_implicant = implicant

        solution.append(leading_implicant)
        cand_implicants.remove(leading_implicant)
        covered_minterms = implicant_coverage[leading_implicant]
        uncovered_minterms -= covered_minterms

    if isinstance(names[0], basestring):
        return BooleanExpression(names, solution)
    return ASTBooleanExpression(names, solution)


class BooleanExpression(object):
    _string = None

    def __init__(self, names, solution):
        self.names = names
        self.solution = solution

    def __str__(self):
        if self._string is None:
            self._string = self._makestring()
        return self._string

    def _makestring(self):
        solution = self.solution

        # Special case--empty solution, always False
        if not solution:
            return 'False'

        names = self.names
        terms = []
        for implicant in self.solution:
            term = []
            for name, truth in zip(names, implicant):
                name = str(name)
                if truth is None:
                    continue
                elif truth:
                    term.append(name)
                else:
                    term.append('not(%s)' % name)

            # Special case--term is all don't cares, always True
            if not term:
                return 'True'

            terms.append('(%s)' % ' and '.join(term))

        return ' or '.join(terms)

    def __call__(self, *args):
        if len(args) != len(self.names):
            raise ValueError("Wrong number of arguments")

        for implicant in self.solution:
            for arg, truth in zip(args, implicant):
                if truth is None:
                    continue
                elif bool(arg) != truth:
                    break
            else:
                # This term is true so expression is true
                return True

        # No true terms found
        return False


class ASTBooleanExpression(BooleanExpression):
    _ast = None

    def ast(self):
        if self._ast is None:
            self._ast = self._make_ast()
        return self._ast

    def _make_ast(self):
        solution = self.solution

        # Special case--empty solution, always False
        if not solution:
            return ast.Name('False', ast.Load())

        propositions = self.names
        terms = []
        for implicant in self.solution:
            term = []
            for proposition, truth in zip(propositions, implicant):
                if truth is None:
                    continue
                elif truth:
                    term.append(proposition)
                else:
                    term.append(ast.UnaryOp(ast.Not(), proposition))

            # Special case--term is all don't cares, always True
            if not term:
                return ast.Name('True', ast.Load())

            terms.append(ast.BoolOp(ast.And(), term))

        expr = ast.BoolOp(ast.Or(), terms)

        def simplify(node):
            if isinstance(node, ast.BoolOp):
                node.values = [simplify(value) for value in node.values]
                if len(node.values) == 1:
                    return node.values[0]
            elif isinstance(node, ast.UnaryOp):
                node.operand = simplify(node.operand)
            return node

        return simplify(expr)

    def _makestring(self):
        return codegen.to_source(self.ast())


def _range_minterms(N):
    for i in xrange(2**N):
        yield _make_minterm(i, N)


def _make_minterm(i, N):
    mask = 1
    implicant = []
    for _ in xrange(N):
        implicant.insert(0, int(bool(i & mask)))
        mask <<= 1
    return tuple(implicant)


def _adjacent(imp1, imp2):
    differences = 0
    match = []
    for m1, m2 in zip(imp1, imp2):
        if m1 == m2:
            match.append(m1)
        elif differences:
            return
        else:
            differences += 1
            match.append(None)

    return tuple(match)


def _covers(implicant, minterm):
    for i, m in zip(implicant, minterm):
        if i is None:
            continue
        if i != m:
            return False
    return True


class _ASTExpression(object):

    def __init__(self, expr):
        tree = ast.parse(expr)
        if len(tree.body) != 1:
            raise SyntaxError("Expression may only contain a single expression.")
        expr_node = tree.body[0]
        if not isinstance(expr_node, ast.Expr):
            raise SyntaxError("Not an expression.")
        self.node = expr_node.value
        self.propositions = {}
        self.propositions_mapping = {}
        self.crawl_expression(self.node)
        self.propositions = self.propositions.values()

    def crawl_expression(self, node):
        if isinstance(node, ast.BoolOp):
            for subtree in node.values:
                self.crawl_expression(subtree)
        elif isinstance(node, ast.UnaryOp):
            assert isinstance(node.op, ast.Not)
            self.crawl_expression(node.operand)
        else:
            s = codegen.to_source(node)
            if s not in self.propositions:
                self.propositions_mapping[node] = node
                self.propositions[s] = node
            else:
                self.propositions_mapping[node] = self.propositions[s]

    def __call__(self, *args):
        assert len(args) == len(self.propositions), "Wronng number of arguments"
        truthtable = dict([pair for pair in zip(self.propositions, args)])

        boolops = {
            ast.And: lambda a, b: a and b,
            ast.Or: lambda a, b: a or b
        }
        def evaluate_node(node):
            if isinstance(node, ast.BoolOp):
                values = [evaluate_node(value) for value in node.values]
                return functools.reduce(boolops[type(node.op)], values)
            elif isinstance(node, ast.UnaryOp):
                return not evaluate_node(node.operand)
            else:
                return truthtable[self.propositions_mapping[node]]

        return evaluate_node(self.node)


def main(argv=sys.argv, out=sys.stdout):
    expr = ' '.join(argv[1:])
    print >> out, str(simplify(expr))


if __name__ == '__main__': #pragma NO COVERAGE
    main()
