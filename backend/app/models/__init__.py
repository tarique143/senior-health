# backend/app/models/__init__.py

# This file makes the 'models' directory a Python package.
# By importing the models here, we can easily access them from other parts of the application.
# For example, we can use 'from app import models' and then access 'models.User'.

from .user import User
from .medication import Medication
from .appointment import Appointment
from .contact import Contact
from .tip import Tip