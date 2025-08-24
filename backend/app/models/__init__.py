# backend/app/models/__init__.py

"""
This file makes the 'models' directory a Python package and centralizes model imports.

By importing all the SQLAlchemy models here, we can use a simpler import statement
in other parts of our application. For example, instead of:
`from app.models.user import User`
`from app.models.medication import Medication`

We can simply use:
`from app import models`
and then access them via `models.User`, `models.Medication`, etc.
This is particularly useful in places like `main.py` where we might need to
create all tables from the `Base.metadata`.
"""

from .appointment import Appointment
from .contact import Contact
from .medication import Medication
from .tip import Tip
from .user import User
