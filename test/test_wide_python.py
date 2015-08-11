
def test_wide_python_build():
    """This test is meant to fail on narrow python builds (common on Mac OS X).

    See https://github.com/RDFLib/rdflib/issues/456 for more information.
    """
    assert len(u'\U0010FFFF') == 1, (
        'You are using a narrow Python build!\n'
        'This means that your Python does not properly support chars > 16bit.\n'
        'On your system chars like c=u"\\U0010FFFF" will have a len(c)==2.\n'
        'As this can cause hard to debug problems with string processing\n'
        '(slicing, regexp, ...) later on, we strongly advise to use a wide\n'
        'Python build in production systems.'
    )
