class RegExpParseError(Exception):
    pass


class Solver:
    _alphabet = ('a', 'b', 'c', '1')
    _operations = ('.', '+', '*')

    @staticmethod
    def _check_list_sizes(threshold: int, *lists: list):
        return all((len(lst) >= threshold for lst in lists))

    @staticmethod
    def _handle_concatenation(re_stack: list, max_word_len: list, max_suffix_len: list):
        if not Solver._check_list_sizes(2, re_stack, max_word_len, max_suffix_len):
            raise RegExpParseError

        re_last = re_stack.pop()
        re_prev = re_stack.pop()

        if re_last == '1':
            re_stack.append(re_prev)
        elif re_prev == '1':
            re_stack.append(re_last)
        else:
            re_stack.append(f'({re_prev}.{re_last})')

        max_word_last = max_word_len.pop()
        max_word_prev = max_word_len.pop()

        max_suffix_last = max_suffix_len.pop()
        max_suffix_prev = max_suffix_len.pop()

        if max_word_last is not None and max_word_prev is not None:
            max_word_len.append(max_word_last + max_word_prev)
        else:
            max_word_len.append(None)

        if max_word_last is not None:
            max_suffix_len.append(max(max_word_last + max_suffix_prev, max_suffix_last))
        else:
            max_suffix_len.append(max_suffix_last)

    @staticmethod
    def _handle_union(re_stack: list, max_word_len: list, max_suffix_len: list):
        if not Solver._check_list_sizes(2, re_stack, max_word_len, max_suffix_len):
            raise RegExpParseError

        re_last = re_stack.pop()
        re_prev = re_stack.pop()

        if re_last == re_prev == '1':
            re_stack.append('1')
        else:
            re_stack.append(f'({re_prev}+{re_last})')

        max_word_last = max_word_len.pop()
        max_word_prev = max_word_len.pop()

        max_suffix_last = max_suffix_len.pop()
        max_suffix_prev = max_suffix_len.pop()

        if max_word_last is None and max_word_prev is None:
            max_word_len.append(None)
        else:
            max_word_len.append(max(0 if max_word_prev is None else max_word_prev,
                                    0 if max_word_last is None else max_word_last))

        max_suffix_len.append(max(max_suffix_prev, max_suffix_last))

    @staticmethod
    def _handle_kleene_star(re_stack: list, max_word_len: list, max_suffix_len: list):
        if not Solver._check_list_sizes(1, re_stack, max_word_len, max_suffix_len):
            raise RegExpParseError

        re_last = re_stack.pop()
        re_stack.append(f'{re_last}*')

        max_word_last = max_word_len.pop()
        max_suffix_last = max_suffix_len.pop()

        if max_word_last is None:
            max_word_len.append(0)
            max_suffix_len.append(max_suffix_last)
        elif re_last == '1':
            max_word_len.append(0)
            max_suffix_len.append(0)
        else:
            max_word_len.append(float('inf'))
            max_suffix_len.append(float('inf'))

    @staticmethod
    def _handle_required_letter(letter: str, re_stack: list, max_word_len: list, max_suffix_len: list):
        re_stack.append(letter)
        max_word_len.append(1)
        max_suffix_len.append(1)

    @staticmethod
    def _handle_empty_letter(re_stack: list, max_word_len: list, max_suffix_len: list):
        re_stack.append('1')
        max_word_len.append(0)
        max_suffix_len.append(0)

    @staticmethod
    def _handle_letter(letter: str, re_stack: list, max_word_len: list, max_suffix_len: list):
        re_stack.append(letter)
        max_word_len.append(None)
        max_suffix_len.append(0)

    @staticmethod
    def has_suffix(regular_expression: str, letter: str, letter_degree: int):
        r"""
        :param regular_expression:
            RE \alpha in reverse polish notation
        :param letter:
            letter `x`
        :param letter_degree:
            degree `k` of letter `x`
        :return:
            True, if in L(`alpha`) exists word `w`, such that `x^k` is a prefix of w
                    $\exists w \in L(\alpha): x^k \sqsupseteq w$
                    ∃w∈L(α): x^k ⊒ w
            False, otherwise
        """

        re_stack = []           # Current RE in infix notation.
        max_word_len = []       # The biggest `r`, s.t. `x^r` is in language. `None` if there is no such r.
        max_suffix_len = []     # The biggest `r`, s.t. `x^r` is a suffix of a word from language.

        for curr_symbol in regular_expression:
            if curr_symbol == letter:
                Solver._handle_required_letter(curr_symbol, re_stack, max_word_len, max_suffix_len)
            elif curr_symbol == '1':
                Solver._handle_empty_letter(re_stack, max_word_len, max_suffix_len)
            elif curr_symbol in Solver._alphabet:
                Solver._handle_letter(curr_symbol, re_stack, max_word_len, max_suffix_len)
            elif curr_symbol == '.':
                Solver._handle_concatenation(re_stack, max_word_len, max_suffix_len)
            elif curr_symbol == '+':
                Solver._handle_union(re_stack, max_word_len, max_suffix_len)
            elif curr_symbol == '*':
                Solver._handle_kleene_star(re_stack, max_word_len, max_suffix_len)
            else:
                raise RegExpParseError

        if len(max_word_len) != 1 or len(max_suffix_len) != 1:
            raise RegExpParseError

        return max_suffix_len[0] >= letter_degree


if __name__ == '__main__':
    alpha, x, k = input().split()
    k = int(k)
    print('YES' if Solver.has_suffix(alpha, x, k) else 'NO')
