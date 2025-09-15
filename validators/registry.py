from __future__ import annotations
import importlib, pkgutil
from validators.base import BaseValidator
def load_all_validators() -> list[BaseValidator]:
    validators: list[BaseValidator] = []
    pkg = "validators.validators"
    for f in pkgutil.iter_modules([pkg.replace(".", "/")]):
        module = importlib.import_module(f"{pkg}.{f.name}")
        if hasattr(module, "get_validator"):
            validators.append(module.get_validator())
    return validators
