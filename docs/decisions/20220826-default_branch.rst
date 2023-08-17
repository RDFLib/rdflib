Default Branch Name
===========================

.. admonition:: Status

   Accepted

Context
-------

In recent years usage of the word ``master`` has become somewhat controversial
[SFC-BNAMING]_ and consequently default branch name of Git repos has become
``main``, both in Git itself [SFC-BNAMING]_ and in Git hosting solutions such as
GitHub [GH-BRANCHES]_.

Decision
--------

RDFLib's
default branch will be renamed from ``master`` to ``main``. This is primarily to stay in line with modern conventions and to adhere to the principle of least surprise.

Consequences
------------

Anticipated negative consequences:

* Some links to old code will be broken.
* Some people's workflow may break unexpectedly and need adjusting.
* Any code and systems reliant on the old default branch name will fail.

Anticipated positive consequences:

* It will become a bit easier to work with RDFLib for developers that are used
  to ``main`` as the default branch.

References
----------

.. [GH-BRANCHES] `GitHub: About the default branch
 <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches#about-the-default-branch>`_
.. [SFC-BNAMING] `Regarding Git and Branch Naming
 <https://sfconservancy.org/news/2020/jun/23/gitbranchname/>`_
