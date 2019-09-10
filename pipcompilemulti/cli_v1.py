"""First version of command line interface"""

import logging

import click

from .options import OPTIONS
from .actions import recompile
from .verify import verify_environments
from .features import FEATURES


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--header', '-h', default='',
              help='File path with custom header text for generated files.')
@FEATURES.bind
def cli(ctx, header):
    """Recompile"""
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    OPTIONS.update({
        'header_file': header or None,
    })
    if ctx.invoked_subcommand is None:
        recompile()


@cli.command()
@click.pass_context
def verify(ctx):
    """
    For each environment verify hash comments and report failures.
    If any failure occured, exit with code 1.
    """
    ctx.exit(0
             if verify_environments()
             else 1)
