import pprint

#
# Implementation of Quine McCluskey algorithm for simplifying boolean
# expressions.
#

def simplify(f, *names):
    N = len(names)

    # Find prime implicants
    prime_implicants = set()

    # Construct the first column
    column = [[] for _ in xrange(N+1)]
    for i in xrange(2**N):
        implicant = make_implicant(i, N)
        if f(*implicant):
            group = 0
            for member in implicant:
                if member:
                    group += 1
            column[group].append(implicant)

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

    print
    print 'Prime implicants'
    pprint.pprint(sorted(prime_implicants))


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


if __name__ == '__main__':
    truths = (4, 5, 6, 8, 9, 10, 13, 0, 7, 15)

    def f(*args):
        proposition = 0
        for arg in args:
            proposition <<= 1
            proposition += arg
        return proposition in truths

    simplify(f, 'A', 'B', 'C', 'D')
