from .earl import EarlReporter

pytest_plugins = [EarlReporter.__module__]
