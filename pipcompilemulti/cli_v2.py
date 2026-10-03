"""Human-friendly interface to pip-compile-multi"""

import functools
import logging
from collections.abc import Callable
from typing import TypeVar

import click

from .actions import recompile
from .config import read_config, read_sections
from .options import OPTIONS
from .types import ConfigSection, OptionValue
from .verify import verify_environments

Result = TypeVar("Result")

logger = logging.getLogger("pip-compile-multi")
DEFAULT_OPTIONS: dict[str, OptionValue] = {
    "directory": "requirements",
    "in_ext": "in",
    "out_ext": "txt",
    "autoresolve": True,
}


@click.group()
def cli() -> None:
    """Human-friendly interface to pip-compile-multi"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")


@cli.command()
def lock() -> None:
    """Lock new dependencies without upgrading."""
    run_configurations(recompile, read_config, upgrade=False)


@cli.command()
@click.argument("packages", nargs=-1)
def upgrade(packages: tuple[str, ...]) -> None:
    """Upgrade locked dependency versions."""
    run_configurations(recompile, read_config, upgrade=True, upgrade_packages=packages)


@cli.command()
@click.pass_context
def verify(ctx: click.Context) -> None:
    """Verify environments."""
    oks = run_configurations(
        skipper(verify_environments),
        read_sections,
    )
    ctx.exit(0 if False not in oks else 1)


def skipper(func: Callable[[], Result]) -> Callable[[], Result]:
    """Decorator that memorizes base_dir, in_ext and out_ext from OPTIONS
    and skips execution for duplicates.
    """

    @functools.wraps(func)
    def wrapped() -> Result:
        """Dummy docstring to make pylint happy."""
        key = (OPTIONS["directory"], OPTIONS["in_ext"], OPTIONS["out_ext"])
        if key not in seen:
            seen[key] = func()
        return seen[key]

    seen: dict[tuple[OptionValue, OptionValue, OptionValue], Result] = {}
    return wrapped


def run_configurations(
    callback: Callable[[], Result],
    sections_reader: Callable[[], list[ConfigSection] | None],
    **overrides: OptionValue,
) -> list[Result]:
    """Parse configurations and execute callback for matching.

    Args:
        callback: Function to execute for each matching section
        sections_reader: Function that returns configuration sections
    """
    sections = sections_reader()
    if sections is None:
        logger.info(
            "Configuration not found in pyproject.toml "
            "or one of .ini files. Running with default settings"
        )
        recompile()
        return []
    elif sections == []:
        logger.info("Configuration does not match current runtime. Exiting")
    results: list[Result] = []
    for section, options in sections:
        OPTIONS.clear()
        OPTIONS.update(DEFAULT_OPTIONS)
        OPTIONS.update(options)
        OPTIONS.update(overrides)
        logger.debug('Running configuration from section "%s". OPTIONS: %r', section, OPTIONS)
        results.append(callback())
    return results


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
