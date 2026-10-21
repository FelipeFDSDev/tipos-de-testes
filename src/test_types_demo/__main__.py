"""Run the local development server with ``python -m test_types_demo``."""

from .app import create_app

create_app().run(debug=True)
