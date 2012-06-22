import unittest


class TestSynthesize(unittest.TestCase):

    def test_all_possible(self, N=3):
        from minbool import range_minterms
        from minbool import synthesize

        def gen_functions():
            n_rows = 2**N
            for n in xrange(3**n_rows):
                truthtable = []
                for _ in xrange(n_rows):
                    truthtable.insert(0, n % 3)
                    n /= 3

                def f(*args):
                    index = 0
                    for arg in args:
                        index <<= 1
                        index += arg
                    result = truthtable[index]
                    if result == 2:
                        return None
                    return result

                yield f

        ord_a = ord('A')
        names = [chr(i) for i in xrange(ord_a, ord_a + N)]
        for f in gen_functions():
            solution = synthesize(f, *names)
            assert str(solution)
            for args in range_minterms(N):
                expected = f(*args)
                if expected is None:
                    continue
                self.assertEqual(expected, solution(*args))
