from rdflib.exceptions import ResolutionForbiddenError
from rdflib.graph import Graph
from rdflib.resolver import PermissiveResolver
import pytest

from test.data import (
    TEST_DATA_DIR,
)


def test_forbidden_resolution():

    jsonld_sample = """
        {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": "La Tour Eiffel",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "Paris",
                "addressRegion": "75007",
                "streetAddress": "Champ de Mars, 5 Avenue Anatole France"
            },
            "description": "Monument emblématique de Paris, la tour Eiffel est une tour de fer puddlé de 324 mètres de hauteur construite par Gustave Eiffel à l’occasion de l’Exposition Universelle de 1889 et qui célébrait le premier centenaire de la Révolution française.",
            "url": "https://www.toureiffel.paris",
            "image": "https://www.toureiffel.paris/sites/default/files/2017-10/monument-landing-header-bg_0.jpg",
            "pricerange": "de 2,5 à 25 euros",
            "telephone": "08 92 70 12 39"
        }
    """

    g = Graph()

    with pytest.raises(
        ResolutionForbiddenError,
        match=r"Resolution of 'https://schema.org' is not allowed",
    ):
        g.parse(data=jsonld_sample, format="json-ld")
