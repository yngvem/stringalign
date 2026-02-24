Installing Stringalign
======================

Installing from PyPI
--------------------

Stringalign is hosted on `PyPI <https://pypi.org/>`_ and can be installed with `pip <https://pip.pypa.io/en/stable/>`_:

.. code:: bash

    pip install stringalign

Alternatively, if you use a project manager like `PDM <https://pdm-project.org/en/latest/>`_,  `uv <https://docs.astral.sh/uv/>`_ or `poetry <https://python-poetry.org/>`_:

.. code:: bash

    [pdm|uv|poetry] add stringalign


Installing from source
----------------------

If you want the latest development version of Stringalign, then you need to compile it yourself.
To do so, you first need to install `Rust <https://rust-lang.org/>`_ (e.g. with  `rustup <https://rustup.rs/>`_), as Stringalign contains a small extension module for performance critical functions.

Once you've installed Rust, you can build and install Stringalign with any tool that supports local installations.
We use PDM for development, so you can e.g. run

.. code:: bash

    git clone https://github.com/yngvem/stringalign.git
    cd stringalign
    pdm install

or build wheels that you install in other environments

.. code:: bash

    git clone https://github.com/yngvem/stringalign.git
    cd stringalign
    pdm build
