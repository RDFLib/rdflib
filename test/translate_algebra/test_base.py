import pandas as pd
import configparser
import os
import sys
from tabulate import tabulate
import logging


def format_text(comment, max_line_length):
    # accumulated line length
    ACC_length = 0
    words = comment.split(" ")
    formatted_text = ""
    for word in words:
        # if ACC_length + len(word) and a space is <= max_line_length
        if ACC_length + (len(word) + 1) <= max_line_length:
            # append the word and a space
            formatted_text = formatted_text + word + " "
            # length = length + length of word + length of space
            ACC_length = ACC_length + len(word) + 1
        else:
            # append a line break, then the word and a space
            formatted_text = formatted_text + "\n" + word + " "
            # reset counter of length to the length of a word and a space
            ACC_length = len(word) + 1
    return formatted_text


class Test:
    def __init__(
        self,
        tc_desc: str,
        expected_result: str = None,
        actual_result: str = None,
        test_number: int = None,
        test_name: str = None,
    ):
        self.test_number = test_number
        self.test_name = test_name
        self.tc_desc = tc_desc
        self.actual_result = actual_result
        self.expected_result = expected_result
        self.yn_passed = False

    def test(self):
        """

        :return:
        """
        assert self.actual_result

        if self.expected_result == self.actual_result:
            self.yn_passed = True


class TestExecution:
    def __init__(self, annotated_tests: bool = False):
        """

        :param annotated_tests: If this flag is set only tests with the prefix "x_test" will be executed.
        """
        test_module_path = os.path.dirname(sys.modules[__class__.__module__].__file__)
        config_path = test_module_path + "/../config.ini"
        self.test_config = configparser.ConfigParser()
        self.test_config.read(config_path)
        self.annotated_tests = annotated_tests
        self.tests = []

    def before_all_tests(self):
        """

        :return:
        """

        print("Executing before_tests ...")

    def before_single_test(self, test_name: str):
        """

        :return:
        """

        print("Executing before_single_tests ...")

    def after_single_test(self):
        """

        :return:
        """

        print("Executing after_single_test")

    def after_all_tests(self):
        """

        :return:
        """

        print("Executing after_tests ...")

    def run_tests(self):
        """

        :return:
        """
        print("Executing tests ...")
        logging.getLogger().setLevel(int(self.test_config.get("TEST", "log_level")))

        self.before_all_tests()
        test_prefix = "test_"
        if self.annotated_tests:
            test_prefix = "x_test_"
        test_functions = [
            func
            for func in dir(self)
            if callable(getattr(self, func)) and func.startswith(test_prefix)
        ]
        try:
            test_number = 1
            for func in test_functions:
                logging.info("Executing test: " + func)
                self.before_single_test(func)
                test_function = getattr(self, func)
                test = test_function()
                test_number += 1
                test.test_name = func
                test.test()
                self.tests.append(test)
                self.after_single_test()
        except Exception as e:
            print(e)
        finally:
            self.after_all_tests()

    def print_test_results(self):
        """

        :return:
        """

        tests_df = pd.DataFrame(
            columns=[
                "test_number",
                "test_passed",
                "test_name",
                "test_case_description",
                "expected_result",
                "actual_result",
            ]
        )
        for test in self.tests:
            if isinstance(test, Test):
                formatted_tc_desc = format_text(test.tc_desc, 100)
                formatted_expected_result = format_text(test.expected_result, 50)
                formatted_actual_result = format_text(test.actual_result, 50)

                tests_df = tests_df.append(
                    {
                        "test_number": test.test_number,
                        "test_passed": test.yn_passed,
                        "test_name": test.test_name,
                        "test_case_description": formatted_tc_desc,
                        "expected_result": formatted_expected_result,
                        "actual_result": formatted_actual_result,
                    },
                    ignore_index=True,
                )

        tests_df.sort_values("test_number", inplace=True)
        pdtabulate = lambda df: tabulate(
            df,
            headers="keys",
            tablefmt="grid",
        )
        print(pdtabulate(tests_df))
