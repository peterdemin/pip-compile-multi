"""Human-friendly interface to pip-compile-multi"""
import functools
import logging

import click

from .options import OPTIONS
from .config import read_config
from .actions import recompile
from .verify import verify_environments


logger = logging.getLogger("pip-compile-multi")


@click.group()
def cli():
    """Human-friendly interface to pip-compile-multi"""
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")


@cli.command()
def lock():
    """Lock new dependencies without upgrading"""
    OPTIONS['upgrade'] = False
    run_configurations(recompile)


@cli.command()
def upgrade():
    """Upgrade locked dependency versions"""
    OPTIONS['upgrade'] = True
    run_configurations(recompile)


@cli.command()
@click.pass_context
def verify(ctx):
    """Upgrade locked dependency versions"""
    oks = run_configurations(ext_skipper(verify_environments))
    ctx.exit(0
             if False in oks
             else 1)


def ext_skipper(func):
    """Decorator that memorizes in_ext and out_ext from OPTIONS
    and skips execution for duplicates."""
    @functools.wraps(func)
    def wrapped():
        """Dummy docstring to make pylint happy."""
        key = (OPTIONS['in_ext'], OPTIONS['out_ext'])
        if key not in seen:
            seen[key] = func()
        return seen[key]
    seen = {}
    return wrapped


def run_configurations(callback):
    """Parse configurations and execute callback for matching."""
    base = dict(OPTIONS)
    sections = read_config()
    if sections is None:
        logger.info("Configuration not found in .ini files. "
                    "Running with default settings")
        recompile()
    elif sections == []:
        logger.info("Configuration does not match current runtime. "
                    "Exiting")
    results = []
    for section, options in sections:
        OPTIONS.clear()
        OPTIONS.update(base)
        OPTIONS.update(options)
        logger.debug("Running configuration from section \"%s\". OPTIONS: %r",
                     section, OPTIONS)
        results.append(callback())
    return results
