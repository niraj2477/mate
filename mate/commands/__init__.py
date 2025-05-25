import typer

from .gcu import main as _gcu
from typing import Annotated
from rich.traceback import install

install(show_locals=True)
app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")


@app.command(no_args_is_help=True, help="Update multiple git repositories to their respective branches")
def gcu(
    path: Annotated[str, typer.Argument(help="Path to the file containing repository paths and branches")],
):
    _gcu(path)


@app.command(no_args_is_help=True, help="test command")
def test():
    typer.echo("This is a test command. It does nothing but print this message.")
