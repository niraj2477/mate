from mate.utils import normalize_path, run_cmd
from mate.utils.console import console
from pathlib import Path
import subprocess
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table


def main(path: str):
    path = normalize_path(path)
    repo_list = []
    messages = []

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                repo_path, branch = line.split(":")
                repo_path = normalize_path(repo_path)
                repo_list.append((repo_path, branch))
            except ValueError:
                messages.append(f"❌ [red]Skipping invalid line: {line}[/red]")

    if not repo_list:
        console.print("❌ [red]No valid repositories found.[/red]")
        return

    console.print(f"📝 [green]Found {len(repo_list)} repositories to update.[/green]\n")

    success_count, fail_count = 0, 0

    with Progress(SpinnerColumn(), TextColumn("[bold blue]{task.description}"), transient=True, console=console) as progress:
        for repo_path, branch in repo_list:
            repo_name = Path(repo_path).name
            task = progress.add_task(f"Processing {repo_name} on {branch}...", start=True)
            try:
                if not (Path(repo_path) / ".git").exists():
                    raise Exception("Not a git repository")
                result = run_cmd(
                    ["git", "-C", repo_path, "remote", "get-url", "origin"],
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    raise Exception("Remote origin not found")

                result = run_cmd(
                    ["git", "-C", repo_path, "branch", "--list", branch],
                    capture_output=True,
                    text=True,
                )
                branch_exists = branch in result.stdout

                current = run_cmd(
                    ["git", "-C", repo_path, "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                )
                current_branch = current.stdout.strip()

                if branch_exists and current_branch == branch:
                    run_cmd(["git", "-C", repo_path, "pull"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                else:
                    run_cmd(["git", "-C", repo_path, "fetch"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    run_cmd(["git", "-C", repo_path, "checkout", branch], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    run_cmd(["git", "-C", repo_path, "pull"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

                # Remove loader before printing result
                progress.remove_task(task)
                console.print(f"✅ [green]{repo_name} updated to branch {branch}.[/green]")
                success_count += 1

            except Exception as e:
                progress.remove_task(task)
                console.print(f"❌ [red]{repo_name} failed on branch {branch}: {e}[/red]")
                fail_count += 1

    console.print()  # spacing

    # Summary Table
    console.print("\n[b]📊 Summary:[/b]\n")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Total")
    table.add_column("Successful")
    table.add_column("Failed")

    table.add_row(
        str(len(repo_list)),
        f"[green]{success_count}[/green]",
        f"[red]{fail_count}[/red]",
    )

    console.print(table)
