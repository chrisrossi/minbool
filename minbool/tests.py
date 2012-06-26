try:
    import unittest2 as unittest
    unittest # stfu pyflakes
except ImportError:
    import unittest


class TestSynthesize(unittest.TestCase):

    def test_all_possible(self, N=3):
        from minbool import _range_minterms
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
            for args in _range_minterms(N):
                expected = f(*args)
                if expected is None:
                    continue
                self.assertEqual(expected, solution(*args))


class TestSimplify(unittest.TestCase):

    def call_fut(self, expr):
        from minbool import simplify as fut
        return fut(expr)

    def test_it(self):
        self.assertEqual(str(self.call_fut('A or B and A')), 'A')
        self.assertEqual(str(self.call_fut('not(A or B and A)')), '(not A)')

    def test_misuse_result(self):
        result = self.call_fut('A or B')
        with self.assertRaises(ValueError):
            result(True)

    def test_always_false(self):
        self.assertEqual(str(self.call_fut('A and not A')), 'False')

    def test_always_true(self):
        self.assertEqual(str(self.call_fut('A or not A')), 'True')

    def test_multiple_statements(self):
        with self.assertRaises(SyntaxError):
            self.call_fut('A; B')

    def test_not_an_expression(self):
        with self.assertRaises(SyntaxError):
            self.call_fut('A = True')

    def test_console_script(self):
        from minbool import main
        from StringIO import StringIO
        output = StringIO()
        main(argv=['simplify', 'A or B and A'], out=output)
        self.assertEqual(output.getvalue(), 'A\n')

    def test_edgecase(self):
        # this input was causing performance to blow up
        result = self.call_fut("A and B or A and C and not C or D and C or E "
                      "and C and F or G and H and B")
        self.assertEqual(str(result), '((A and B) or (B and G and H) or '
                         '(C and D) or (C and E and F))')
