# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import stringalign

project = "Stringalign"
copyright = "2025, Yngve Mardal Moe & Marie Roald"
author = "Yngve Mardal Moe & Marie Roald"
release = stringalign.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.bibtex",
    "sphinx_book_theme",
    "sphinx_togglebutton",
    "sphinx_gallery.gen_gallery",
]

templates_path = ["_templates"]
exclude_patterns: list[str] = []
bibtex_bibfiles = ["bibliography.bib"]
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
sphinx_gallery_conf = {
    "examples_dirs": "../../examples/scripts",
    "gallery_dirs": "auto_examples",
    "capture_repr": ("_repr_html_", "__repr__"),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_logo = "images/bunting_flat.svg"
html_favicon = "images/favicon.svg"
