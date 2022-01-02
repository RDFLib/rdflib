import os


def test_issue679_trig_export_reopen(get_dataset):

    # STATUS: FIXED? no longer an issue

    #  trig export of multiple graphs assigns wrong prefixes to prefixedNames #679

    # I wanted to add that I see this behavior even in the case of parsing a dataset
    # with a single graph in nquads format and serializing as trig with no special characters.

    nquads = open(
        os.path.join(
            os.path.dirname(__file__), "..", "consistent_test_data", "sportquads.nq"
        )
    ).read()

    ds = get_dataset
    ds.parse(data=nquads, format="nquads")
    # logger.debug(
    #     f"test_trig_export_reopen trig\n{ds.serialize(format='trig')}"
    # )
