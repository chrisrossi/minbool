import pprint

#
# Implementation of Quine McCluskey algorithm for simplifying boolean
# expressions.
#

def simplify(f, *names):
    N = len(names)

    # Construct truth table
    truthtable = {}
    for minterm in range_minterms(N):
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
    column_no = 1
    while not done:
        print "Column", column_no
        column_no += 1
        pprint.pprint(column)
        print

        done = True
        next_column  = [[] for _ in xrange(N+1)]
        matches = [[False for _ in xrange(len(column[n]))] for n in xrange(N+1)]
        for n in xrange(N):
            this_group = column[n]
            next_group = column[n+1]
            for i, implicant in enumerate(this_group):
                for j, candidate in enumerate(next_group):
                    match = adjacent(implicant, candidate)
                    if match:
                        matches[n][i] = matches[n+1][j] = True
                        group = 0
                        for member in match:
                            if member:
                                group += 1
                        next_column[group].append(match)
                        done = False

        for i in xrange(N):
            for j in xrange(len(matches[i])):
                if not matches[i][j]:
                    prime_implicants.add(tuple(column[i][j]))

        column = next_column

    print 'Prime implicants'
    pprint.pprint(sorted(prime_implicants))
    print

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
            if covers(implicant, minterm):
                covering_implicants.append(implicant)
                implicant_coverage[implicant].add(minterm)

    # find essential implicants
    cand_implicants = set(prime_implicants)
    solution = []
    for minterm, covering_implicants in minterm_coverage.items():
        if len(covering_implicants) == 1:
            # covering implicant is essential
            implicant = covering_implicants[0]
            solution.append(implicant)
            cand_implicants.remove(implicant)
            covered_minterms = implicant_coverage[implicant]
            uncovered_minterms -= covered_minterms

    print "Essential implicants"
    pprint.pprint(solution)
    print

    print "Uncovered minterms"
    pprint.pprint(uncovered_minterms)
    print

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

    print "Final solution"
    pprint.pprint(solution)
    print

    return BooleanExpression(names, solution)


def range_minterms(N):
    for i in xrange(2**N):
        yield make_implicant(i, N)


def make_implicant(i, N):
    mask = 1
    implicant = []
    for _ in xrange(N):
        implicant.insert(0, int(bool(i & mask)))
        mask <<= 1
    return tuple(implicant)


def adjacent(imp1, imp2):
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

    return match


def covers(implicant, minterm):
    for i, m in zip(implicant, minterm):
        if i is None:
            continue
        if i != m:
            return False
    return True


class BooleanExpression(object):

    def __init__(self, names, solution):
        self.names = names
        self.solution = solution

    def __str__(self):
        names = self.names
        terms = []
        for implicant in self.solution:
            term = []
            for name, truth in zip(names, implicant):
                if truth is None:
                    continue
                elif truth:
                    term.append(name)
                else:
                    term.append('not(%s)' % name)
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


if __name__ == '__main__':
    truths = (4, 5, 6, 8, 9, 10, 13)
    dontcare = (0, 7, 15)

    def f(*args):
        proposition = 0
        for arg in args:
            proposition <<= 1
            proposition += arg
        if proposition in dontcare:
            return None
        else:
            return proposition in truths

    solution = simplify(f, 'A', 'B', 'C', 'D')
    print str(solution)

    for i in xrange(16):
        if i in dontcare:
            continue
        args = make_implicant(i, 4)
        assert solution(*args) == f(*args)


