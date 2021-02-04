"""The current stable version of command line interface."""

import os
import sys
import logging
from traceback import print_exception

import click

from .actions import recompile
from .verify import verify_environments
from .features import FEATURES


THIS_FILE = os.path.abspath(__file__)


@click.group(invoke_without_command=True)
@click.pass_context
@FEATURES.bind
def cli(ctx):
    """Recompile"""
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    sys.excepthook = exception_hook
    if ctx.invoked_subcommand is None:
        recompile()


@cli.command()
@click.pass_context
@FEATURES.bind
def verify(ctx):
    """
    For each environment verify hash comments and report failures.
    If any failure occured, exit with code 1.
    """
    sys.excepthook = exception_hook
    ctx.exit(0
             if verify_environments()
             else 1)


def exception_hook(exctype, value, traceback):
    """Strip exception printout above this module."""
    print_exception(exctype, value, trim_traceback(traceback))


def trim_traceback(traceback):
    """Trim traceback top so it starts with this module.

    Return original traceback if this module is not found.
    """
    level = 0
    new_traceback = traceback
    while new_traceback is not None:
        file_path = new_traceback.tb_frame.f_code.co_filename
        if THIS_FILE.startswith(file_path):
            return new_traceback
        level += 1
        new_traceback = new_traceback.tb_next
    return traceback


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
