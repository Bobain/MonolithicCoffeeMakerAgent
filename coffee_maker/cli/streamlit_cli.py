"""CLI commands for Streamlit app."""

import click
import subprocess
import sys
from pathlib import Path


@click.command()
@click.option("--port", default=8501, help="Port to run on")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
def ace_ui(port: int, reload: bool):
    """Launch ACE configuration & monitoring UI."""
    app_path = Path(__file__).parent.parent / "streamlit_app" / "app.py"

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        str(port),
    ]

    if reload:
        cmd.append("--server.runOnSave=true")

    click.echo(f"🚀 Launching ACE UI on http://localhost:{port}")
    subprocess.run(cmd)


if __name__ == "__main__":
    ace_ui()
