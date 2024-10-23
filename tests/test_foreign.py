import unittest

from pyswip import (
    Prolog,
    registerForeign,
    PL_foreign_context,
    PL_foreign_control,
    PL_FIRST_CALL,
    PL_REDO,
    PL_PRUNED,
    PL_retry,
    PL_FA_NONDETERMINISTIC,
    Variable,
)


class MyTestCase(unittest.TestCase):
    def test_deterministic_foreign(self):
        def hello(t):
            print("Hello,", t)

        hello.arity = 1

        registerForeign(hello)

        Prolog.assertz("mother(emily,john)")
        Prolog.assertz("mother(emily,gina)")
        result = list(Prolog.query("mother(emily,X), hello(X)"))
        self.assertEqual(len(result), 2, "Query should return two results")
        for name in ("john", "gina"):
            self.assertTrue(
                {"X": name} in result, "Expected result  X:{} not present".format(name)
            )

    def test_deterministic_foreign_automatic_arity(self):
        def hello(t):
            print("Hello,", t)

        Prolog.register_foreign(hello, module="autoarity")

        Prolog.assertz("autoarity:mother(emily,john)")
        Prolog.assertz("autoarity:mother(emily,gina)")
        result = list(Prolog.query("autoarity:mother(emily,X), autoarity:hello(X)"))
        self.assertEqual(len(result), 2, "Query should return two results")
        for name in ("john", "gina"):
            self.assertTrue(
                {"X": name} in result, "Expected result  X:{} not present".format(name)
            )

    def test_nondeterministic_foreign(self):
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
        result = list(Prolog.query("nondet(X)"))

        self.assertEqual(len(result), 10, "Query should return 10 results")
        for i in range(10):
            self.assertTrue(
                {"X": i} in result, "Expected result  X:{} not present".format(i)
            )

    def test_nondeterministic_foreign_autoarity(self):
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

        Prolog.register_foreign(nondet, module="autoarity", nondeterministic=True)
        result = list(Prolog.query("autoarity:nondet(X)"))

        self.assertEqual(len(result), 10, "Query should return 10 results")
        for i in range(10):
            self.assertTrue(
                {"X": i} in result, "Expected result  X:{} not present".format(i)
            )

    def test_atoms_and_strings_distinction(self):
        test_string = "string"

        def get_str(string):
            string.value = test_string

        def test_for_string(string, test_result):
            test_result.value = test_string == string.decode("utf-8")

        get_str.arity = 1
        test_for_string.arity = 2

        registerForeign(get_str)
        registerForeign(test_for_string)

        result = list(Prolog.query("get_str(String), test_for_string(String, Result)"))
        self.assertEqual(
            result[0]["Result"],
            "true",
            "A string return value should not be converted to an atom.",
        )

    def test_unifying_list_correctly(self):
        variable = Variable()
        variable.value = [1, 2]
        self.assertEqual(variable.value, [1, 2], "Lists should be unifyed correctly.")

    def test_nested_lists(self):
        def get_list_of_lists(result):
            result.value = [[1], [2]]

        get_list_of_lists.arity = 1

        registerForeign(get_list_of_lists)

        result = list(Prolog.query("get_list_of_lists(Result)"))
        self.assertTrue(
            {"Result": [[1], [2]]} in result,
            "Nested lists should be unified correctly as return value.",
        )

    def test_dictionary(self):
        result = list(Prolog.query("X = dict{key1:value1 , key2: value2}"))
        dict = result[0]
        self.assertTrue(
            {"key1": "value1", "key2": "value2"} == dict["X"],
            "Dictionary should be returned as a dictionary object",
        )

    def test_empty_dictionary(self):
        result = list(Prolog.query("X = dict{}"))
        dict = result[0]
        self.assertTrue(
            dict["X"] == {},
            "Empty dictionary should be returned as an empty dictionary object",
        )

    def test_nested_dictionary(self):
        result = list(Prolog.query("X = dict{key1:nested{key:value} , key2: value2}"))
        dict = result[0]
        self.assertTrue(
            {"key1": {"key": "value"}, "key2": "value2"} == dict["X"],
            "Nested Dictionary should be returned as a nested dictionary object",
        )


if __name__ == "__main__":
    unittest.main()
