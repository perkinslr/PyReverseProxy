import click
import functools
click.core._verify_python3_env = lambda *x: None

_main = click.core.BaseCommand.main


@functools.partial(setattr, click.core.BaseCommand, 'main')
def main(self, args: []=None, prog_name: str=None, complete_var: str=None, standalone_mode: bool=True, **extra):
    if args and prog_name is None:
        prog_name = args[0]
        args = args[1:]
    else:
        args = None

    if not standalone_mode:
        ctx = self.make_context(prog_name, args)
        with ctx:
            self.invoke(ctx)
            return ctx

    return _main(self, args, prog_name, complete_var, standalone_mode, **extra)

