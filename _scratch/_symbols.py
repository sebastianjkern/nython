# %%
import json

# %%
def __getImportedNames (module):
    names = module.__all__ if hasattr(module, '__all__') else dir(module)
    return [name for name in names if not name.startswith('_')]

print(__getImportedNames(json))
print(__getImportedNames(__builtins__))

