"""Human-friendly interface to pip-compile-multi"""
import functools
import logging

import click

from .options import OPTIONS
from .config import read_config, read_sections
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
    run_configurations(recompile, read_config)


@cli.command()
def upgrade():
    """Upgrade locked dependency versions"""
    OPTIONS['upgrade'] = True
    OPTIONS['upgrade_packages'] = []
    run_configurations(recompile, read_config)


@cli.command()
@click.pass_context
def verify(ctx):
    """Upgrade locked dependency versions"""
    oks = run_configurations(
        skipper(verify_environments),
        read_sections,
    )
    ctx.exit(0
             if False not in oks
             else 1)


def skipper(func):
    """Decorator that memorizes base_dir, in_ext and out_ext from OPTIONS
    and skips execution for duplicates.
    """
    @functools.wraps(func)
    def wrapped():
        """Dummy docstring to make pylint happy."""
        key = (OPTIONS['base_dir'], OPTIONS['in_ext'], OPTIONS['out_ext'])
        if key not in seen:
            seen[key] = func()
        return seen[key]
    seen = {}
    return wrapped


def run_configurations(callback, sections_reader):
    """Parse configurations and execute callback for matching."""
    base = {
        'base_dir': 'requirements',
        'in_ext': 'in',
        'out_ext': 'txt',
    }
    sections = sections_reader()
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
