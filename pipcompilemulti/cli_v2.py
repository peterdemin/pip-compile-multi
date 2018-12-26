"""Human-friendly interface to pip-compile-multi"""
import logging

import click

from .options import OPTIONS
from .config import read_config
from .actions import recompile
from .verify import verify_environments


logger = logging.getLogger("pip-compile-multi")
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
    base = dict(OPTIONS)
    sections = read_config()
    if sections is None:
        logger.info("Configuration not found in requirements.ini. "
                    "Running with default settings")
        recompile()
    elif sections == []:
        logger.info("Configuration does not match current runtime. "
                    "Exiting")
    for section, options in sections:
        logger.info("Running configuration from section %s",
                    section)
        OPTIONS.clear()
        OPTIONS.update(base)
        OPTIONS.update(options)
        logger.debug(OPTIONS)
        recompile()


@cli.command()
def upgrade():
    """Upgrade locked dependency versions"""
    OPTIONS['upgrade'] = True
    recompile()


@cli.command()
@click.pass_context
def verify(ctx):
    """Upgrade locked dependency versions"""
    OPTIONS['upgrade'] = True
    ctx.exit(0
             if verify_environments()
             else 1)
