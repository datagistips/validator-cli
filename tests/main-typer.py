import typer

app = typer.Typer()

@app.command()
def control(inputfile: str, schemafile:str, directory: bool = False):
    typer.echo(f"{directory}")
    typer.echo(f"{schemafile}")
    typer.echo(f"{directory}")

@app.command()
def transform(inputfile: str, mappingfile:str, directory: bool = False):
    typer.echo(f"{directory}")
    typer.echo(f"{mappingfile}")
    typer.echo(f"{directory}")


if __name__ == "__main__":
    app()
