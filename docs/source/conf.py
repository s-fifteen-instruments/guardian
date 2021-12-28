# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'Guardian'
copyright = '2021, S-Fifteen'
author = 'S-Fifteen'

release = '0.7'
version = '0.7.0'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx_tabs.tabs' # https://sphinx-tabs.readthedocs.io/en/latest/
    ]

#autoapi_dirs = ['../rest/app/api/api_v1/endpoints']
#autoapi_add_toctree_entry = False

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None)
}

intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'

# sphinx-tabs configuration
sphinx_tabs_disable_tab_closing = True
# sphinx_tabs_disable_css_loading = True