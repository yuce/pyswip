import unittest

from pyswip import Prolog, registerForeign, PL_foreign_context, PL_foreign_control, PL_FIRST_CALL, PL_REDO, PL_PRUNED, PL_retry, PL_FA_NONDETERMINISTIC, Variable


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
    
    def test_atoms_and_strings_distinction(self):
        test_string = "string"

        def get_str(string):
            string.value = test_string
        
        def test_for_string(string, test_result):
            test_result.value = (test_string == string.decode('utf-8'))

        get_str.arity = 1
        test_for_string.arity = 2

        registerForeign(get_str)
        registerForeign(test_for_string)

        prolog = Prolog()
        
        result = list(prolog.query("get_str(String), test_for_string(String, Result)"))
        self.assertEqual(result[0]['Result'], 'true', 'A string return value should not be converted to an atom.')
    
    def test_unifying_list_correctly(self):
        variable = Variable()
        variable.value = [1, 2]
        self.assertEqual(variable.value, [1, 2], 'Lists should be unifyed correctly.')

    def test_nested_lists(self):
        def get_list_of_lists(result):
            result.value = [[1], [2]]

        get_list_of_lists.arity = 1

        registerForeign(get_list_of_lists)

        prolog = Prolog()
        
        result = list(prolog.query("get_list_of_lists(Result)"))
        self.assertTrue({'Result': [[1], [2]]} in result, 'Nested lists should be unified correctly as return value.')

    def test_dictionary(self):
        prolog = Prolog()
        result = list(prolog.query("X = dict{value1:value1 , value2: value2}"))
        dict = result[0]
        print(dict)
        self.assertTrue({"value1":"value1", "value2":"value2"} == dict["X"], "Dictionary should be returned as a dictionary object")



if __name__ == '__main__':
    unittest.main()
