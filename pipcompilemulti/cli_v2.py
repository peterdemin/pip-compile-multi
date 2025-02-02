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
@click.option('-u', '--uv', is_flag=True, help='Use uv for faster version resolution')
def lock(uv):
    """Lock new dependencies without upgrading.
    
    Use uv for faster version resolution if --uv is passed.
    """
    OPTIONS['upgrade'] = False
    OPTIONS['use_uv'] = bool(uv)
    run_configurations(recompile, read_config, use_uv=OPTIONS['use_uv'])

@cli.command()
@click.option('-u', '--uv', is_flag=True, help='Use uv for upgrading dependencies')
def upgrade(uv):
    """Upgrade locked dependency versions.
    
    Use uv for faster version resolution if --uv is passed.
    """
    OPTIONS['upgrade'] = True
    OPTIONS['upgrade_packages'] = []
    OPTIONS['use_uv'] = bool(uv)
    run_configurations(recompile, read_config, use_uv=OPTIONS['use_uv'])

@cli.command()
@click.option('-u', '--uv', is_flag=True, help='Use uv for locking requirements')
@click.pass_context
def verify(ctx, uv):
    """Verify environments.
    
    Use uv for faster version resolution if --uv is passed.
    """
    OPTIONS['use_uv'] = bool(uv)
    oks = run_configurations(
        skipper(verify_environments),
        read_sections,
        use_uv=OPTIONS['use_uv']
    )
    ctx.exit(0 if False not in oks else 1)

def skipper(func):
    """Decorator that memorizes base_dir, in_ext and out_ext from OPTIONS
    and skips execution for duplicates."""
    @functools.wraps(func)
    def wrapped():
        """Dummy docstring to make pylint happy."""
        key = (OPTIONS['base_dir'], OPTIONS['in_ext'], OPTIONS['out_ext'])
        if key not in seen:
            seen[key] = func()
        return seen[key]
    seen = {}
    return wrapped

def run_configurations(callback, sections_reader, use_uv=False):
    """Parse configurations and execute callback for matching sections.
    
    Args:
        callback: Function to execute for each matching section
        sections_reader: Function that returns configuration sections
        use_uv: Whether to use uv instead of pip-compile for dependency resolution
    
    Returns:
        List of results from callback executions
    """
    base = {
        'base_dir': 'requirements',
        'in_ext': 'in',
        'out_ext': 'txt',
        'autoresolve': True,
        'use_uv': use_uv,
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

if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
