from invoke import Collection, task
from estcp_project import project_root
from pathlib import Path

work_dir_pth = Path(__file__).parent

ns = Collection()

@task
def build_book(ctx):
    """
    build jupyter-book from book in build
    """
    with ctx.cd(str(work_dir_pth)):
        ctx.run(f"jupyter-book build {work_dir_pth}/book --path-output {work_dir_pth}/build", echo=True)
ns.add_task(build_book)

@task#(pre=[build_book])
def _git_hook(ctx, *_, **__): # just consumes the (file) args so precommit git hook works
    """
    git hook to commit contents of book to dvc
    """
    with ctx.cd(str(work_dir_pth)):
        ctx.run(f"dvc commit ${work_dir_pth}/dvc.yaml:book -f", echo=True)
        ctx.run(f"git add    ${work_dir_pth}/dvc.lock",         echo=True)

# share
