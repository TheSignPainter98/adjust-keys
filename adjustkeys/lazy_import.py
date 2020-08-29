# Copyright (C) Edward Jones

from .exceptions import AdjustKeysException
from importlib import import_module

class LazyImport:
    def __init__(self, *impNames:str):
        if len(impNames) == 0:
            raise AdjustKeysException('Lazy import called without a module to import!')
        if len(impNames) >= 2:
            self.modName:str = '.'.join(impNames[:-1])
            self.impName:str = impNames[-1]
        else:
            self.modName:str = impNames[0]
            self.impName:str = None

        self.mod:module = None

    def _imp_mod(self):
        if self.mod is None:
            self.mod = import_module(self.modName)

    def __getattr__(self, attr:str) -> object:
        self._imp_mod()
        if self.impName is not None:
            return getattr(getattr(self.mod, self.impName), attr)
        else:
            return getattr(self.mod, attr)

    def __call__(self, *args, **kwargs) -> object:
        self._imp_mod()
        if self.impName is None:
            raise AdjustKeysException('Attempted to call module as function, lazy import requires an import name as well as a module name before it can be called.')
        return getattr(self.mod, self.impName)(*args, **kwargs)

    def __str__(self) -> str:
        return '<LazyImport: %s, importPerformed: %s>' %(self.modName, self.mod is not None)
