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
        ctx.run(f"jupyter-book build {work_dir_pth / 'book'} --path-output {work_dir_pth / 'build'}", echo=True)
ns.add_task(build_book)

@task#(pre=[build_book])
def _git_hook(ctx, *_, **__): # using magicinvoke, just consumes the (file) args so precommit git hook works
    # https://github.com/pyinvoke/invoke/issues/378
    """
    git hook to commit contents of book to dvc
    """
    with ctx.cd(str(work_dir_pth)):
        ctx.run(f"dvc commit {work_dir_pth / 'dvc.yaml'}:book -f", echo=True)
        ctx.run(f"git add    {work_dir_pth / 'dvc.lock'}",         echo=True)
ns.add_task(_git_hook)

@task
def share(ctx, ):
    """
    copy built book to share location
    """
    cur_branch = ctx.run('git rev-parse --abbrev-ref HEAD', hide='out').stdout.replace('\n','')
    cur_hash   = ctx.run('git rev-parse              HEAD', hide='out').stdout.replace('\n','')
    import yaml
    branch_loc = Path(yaml.safe_load(open(work_dir_pth / 'config.yml'))['share']['loc']) / cur_branch
    hash_loc   = Path(yaml.safe_load(open(work_dir_pth / 'config.yml'))['share']['loc']) / cur_hash
    if branch_loc.exists(): branch_loc.unlink(); branch_loc.mkdir(parents=True)
    if   hash_loc.exists():   hash_loc.unlink();   hash_loc.mkdir(parents=True)
    book_loc = work_dir_pth / 'build' / '_build' / 'html'
    from shutil import copytree
    copytree(book_loc, branch_loc)
    copytree(book_loc, hash_loc)
ns.add_task(share)
