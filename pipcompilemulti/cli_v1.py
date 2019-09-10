"""The current stable version of command line interface."""

import logging

import click

from .actions import recompile
from .verify import verify_environments
from .features import FEATURES


@click.group(invoke_without_command=True)
@click.pass_context
@FEATURES.bind
def cli(ctx):
    """Recompile"""
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
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
