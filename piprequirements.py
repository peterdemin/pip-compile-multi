"""Human-friendly interface to pip-compile-multi"""
import logging
import click
from pipcompilemulti import recompile, OPTIONS


MORE_DEFAULTS = {
    'add_hashes': [],
    'include_names': [],
}


@click.group()
def cli():
    """Human-friendly interface to pip-compile-multi"""
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    OPTIONS.update(MORE_DEFAULTS)


@cli.command()
def lock():
    """Lock new dependencies without upgrading"""
    OPTIONS['upgrade'] = False
    recompile()


@cli.command()
def upgrade():
    """Upgrade locked dependency versions"""
    OPTIONS['upgrade'] = True
    recompile()
