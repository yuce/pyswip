import unittest

from pyswip import Prolog, registerForeign, PL_foreign_context, PL_foreign_control, PL_FIRST_CALL, PL_REDO, PL_PRUNED, PL_retry, PL_FA_NONDETERMINISTIC


class MyTestCase(unittest.TestCase):
    def test_deterministic_foreign(self):
        def hello(t):
            print("Hello,", t)

        hello.arity = 1

        registerForeign(hello)

        prolog = Prolog()
        prolog.assertz("father(michael,john)")
        prolog.assertz("father(michael,gina)")
        result = list(prolog.query("father(michael,X), hello(X)"))
        self.assertEqual(len(result), 2, 'Query should return two results')
        for name in ('john', 'gina'):
            self.assertTrue({'X': name} in result, 'Expected result  X:{} not present'.format(name))

    def test_nondeterministic_foreign(self):
        prolog = Prolog()

        def nondet(a, context):
            control = PL_foreign_control(context)
            context = PL_foreign_context(context)
            if control == PL_FIRST_CALL:
                context = 0
                a.unify(int(context))
                context += 1
                return PL_retry(context)
            elif control == PL_REDO:
                a.unify(int(context))
                if context == 10:
                    return False
                context += 1
                return PL_retry(context)
            elif control == PL_PRUNED:
                pass
        nondet.arity = 1
        registerForeign(nondet, flags=PL_FA_NONDETERMINISTIC)
        result = list(prolog.query("nondet(X)"))

        self.assertEqual(len(result), 10, 'Query should return 10 results')
        for i in range(10):
            self.assertTrue({'X': i} in result, 'Expected result  X:{} not present'.format(i))



if __name__ == '__main__':
    unittest.main()
