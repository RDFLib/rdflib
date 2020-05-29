# -*- coding: utf-8 -*-

import doctest
import logging
import re

from nose.plugins import Plugin

log = logging.getLogger('nose.plugins.doctest.ignore_unicode')

IGNORE_UNICODE = doctest.register_optionflag('IGNORE_UNICODE')


class _UnicodeOutputCheck(object):
    _literal_re = re.compile(r"(\W|^)[uU]([rR]?[\'\"])", re.UNICODE)

    def __init__(self, check_output):
        self.check_output = check_output

    def _remove_u_prefixes(self, txt):
        return re.sub(self._literal_re, r'\1\2', txt)

    def __call__(self, want, got, optionflags):
        if optionflags & IGNORE_UNICODE:
            want = self._remove_u_prefixes(want)
            got = self._remove_u_prefixes(got)
        res = self.check_output(want, got, optionflags)
        return res


class DoctestIgnoreUnicode(Plugin):
    """
    This plugin adds support for '#doctest +IGNORE_UNICODE' option that
    makes DocTestCase think u'foo' == 'foo'.
    """
    name = 'doctest-ignore-unicode'

    def prepareTestCase(self, case):
        self._patchTestCase(case.test)

    def _patchTestCase(self, case):
        # Monkey patch the output checker.
        if hasattr(case, '_dt_checker'):
            checker = case._dt_checker or doctest.OutputChecker()
            checker.check_output = _UnicodeOutputCheck(checker.check_output)
            case._dt_checker = checker
        return case
