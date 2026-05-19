"""Compile-check all 22 strategy files."""
import py_compile, os

dir = 'strategies'
errors = []
for f in sorted(os.listdir(dir)):
    if f.endswith('.py') and f != '__init__.py':
        path = os.path.join(dir, f)
        try:
            py_compile.compile(path, doraise=True)
            print(f'OK  {f}')
        except py_compile.PyCompileError as e:
            print(f'ERR {f}: {e}')
            errors.append(f)

if errors:
    print(f'\n{len(errors)} errors found')
    exit(1)
else:
    print(f'\nAll 22 strategy files OK')