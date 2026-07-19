from .directives import register_sphinx_version_notice_directives
from .roles import register_sphinx_reference_roles

# register Sphinx roles and directives - always required
register_sphinx_reference_roles()
register_sphinx_version_notice_directives()
