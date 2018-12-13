import unittest
from main import Solver, RegExpParseError


class TestSolverMethods(unittest.TestCase):
    def assert_lists(self, func, max_word_len: list, max_suffix_len: list,
                     word_expected: list, suffix_expected: list):
        func(max_word_len, max_suffix_len)
        self.assertEqual(max_word_len, word_expected)
        self.assertEqual(max_suffix_len, suffix_expected)

    def test_handle_concatenation(self):
        with self.assertRaises(RegExpParseError):
            Solver._handle_concatenation([], [])
        with self.assertRaises(RegExpParseError):
            Solver._handle_concatenation([1], [2, 3])

        self.assert_lists(Solver._handle_concatenation, [None, None], [1, 1], [None], [1])
        self.assert_lists(Solver._handle_concatenation, [None, 1], [2, 1], [None], [3])
        self.assert_lists(Solver._handle_concatenation, [3, 4], [6, 7], [7], [10])

    def test_handle_union(self):
        with self.assertRaises(RegExpParseError):
            Solver._handle_union([], [])
        with self.assertRaises(RegExpParseError):
            Solver._handle_union([1], [2, 3])

        self.assert_lists(Solver._handle_union, [None, None], [1, 2], [None], [2])
        self.assert_lists(Solver._handle_union, [2, None], [4, 2], [2], [4])
        self.assert_lists(Solver._handle_union, [None, 2], [3, 3], [2], [3])
        self.assert_lists(Solver._handle_union, [5, 2], [6, 3], [5], [6])

    def test_handle_kleene_star(self):
        with self.assertRaises(RegExpParseError):
            Solver._handle_union([], [])
        with self.assertRaises(RegExpParseError):
            Solver._handle_union([None], [])

        self.assert_lists(Solver._handle_kleene_star, [None], [2], [0], [2])
        self.assert_lists(Solver._handle_kleene_star, [0], [2], [0], [2])
        self.assert_lists(Solver._handle_kleene_star, [1], [2], [float('inf')], [float('inf')])
        self.assert_lists(Solver._handle_kleene_star, [3], [3], [float('inf')], [float('inf')])

    def test_handle_required_letter(self):
        self.assert_lists(Solver._handle_required_letter, [], [], [1], [1])
        self.assert_lists(Solver._handle_required_letter, [2, 2], [3, 3], [2, 2, 1], [3, 3, 1])
        self.assert_lists(Solver._handle_required_letter, [None], [0], [None, 1], [0, 1])

    def test_handle_empty_letter(self):
        self.assert_lists(Solver._handle_empty_letter, [], [], [0], [0])
        self.assert_lists(Solver._handle_empty_letter, [2, 2], [3, 3], [2, 2, 0], [3, 3, 0])
        self.assert_lists(Solver._handle_empty_letter, [None], [0], [None, 0], [0, 0])

    def test_handle_letter(self):
        self.assert_lists(Solver._handle_letter, [], [], [None], [0])
        self.assert_lists(Solver._handle_letter, [2, 2], [3, 3], [2, 2, None], [3, 3, 0])
        self.assert_lists(Solver._handle_letter, [None], [0], [None, None], [0, 0])

    def test_has_suffix(self):
        with self.assertRaises(RegExpParseError):
            Solver.has_suffix('', 'a', 0)
        with self.assertRaises(RegExpParseError):
            Solver.has_suffix('aaaa', 'b', 30)
        with self.assertRaises(RegExpParseError):
            Solver.has_suffix('a+b', 'c', 2)
        with self.assertRaises(RegExpParseError):
            Solver.has_suffix('.', '1', 3)

        self.assertFalse(Solver.has_suffix('ab+c.aba.*.bac.+.+*', 'a', 2))
        self.assertFalse(Solver.has_suffix('1*', 'a', 2))
        self.assertFalse(Solver.has_suffix('1*', 'c', 500))
        self.assertFalse(Solver.has_suffix('a*b+', 'b', 2))
        self.assertFalse(Solver.has_suffix('ab+c+', 'b', 13))
        self.assertFalse(Solver.has_suffix('ab.c.', 'c', 2))
        self.assertFalse(Solver.has_suffix('ab+c.', 'b', 1))
        self.assertFalse(Solver.has_suffix('ab+c.bc+a.+ca+b.+*', 'b', 3))

        self.assertTrue(Solver.has_suffix('acb..bab.c.*.ab.ba.+.+*a.', 'c', 0))
        self.assertTrue(Solver.has_suffix('1*', 'a', 0))
        self.assertTrue(Solver.has_suffix('a*b+', 'b', 1))
        self.assertTrue(Solver.has_suffix('ab+*1.', 'b', 3))
        self.assertTrue(Solver.has_suffix('ab+c+', 'b', 1))
        self.assertTrue(Solver.has_suffix('ab+c+*', 'b', 100))
        self.assertTrue(Solver.has_suffix('ab+c.', 'b', 0))
        self.assertTrue(Solver.has_suffix('ab+c.bc+a.+ca+b.+*', 'a', 1))
