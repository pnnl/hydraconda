from invoke import Collection, task
from estcp_project import project_root
from pathlib import Path

work_dir_pth = Path(__file__).parent

ns = Collection()

#@task
def _(ctx):
    ctx.run(f"jupyter notebook")
#ns.add_task(test)

# not needed i think b/c kernels are installed on every jupyter cmd: jupter_config.py
# @task
# def install_kernels(ctx):
#     """
#     install project jupyter kernels
#     """
#     from notebooking_kernels import KernelSpecManager
#     ksm = KernelSpecManager()
#     #ksm.install_kernel_specs()
# ns.add_task(install_kernels)


@task
def build_book(ctx):
    """
    build jupyter-book from book in build
    """
    with ctx.cd(str(work_dir_pth)):
        ctx.run(f"jupyter-book build {work_dir_pth / 'book'} --path-output {work_dir_pth / 'build'}", echo=True)
ns.add_task(build_book)


@task(pre=[build_book])
def _git_hook(ctx, *_, **__): # using magicinvoke, just consumes the (file) args so precommit git hook works
    # https://github.com/pyinvoke/invoke/issues/378
    """
    git hook to commit contents of book to dvc
    """
    with ctx.cd(str(work_dir_pth)):
        ctx.run(f"dvc commit {work_dir_pth / 'dvc.yaml'}:book -f", echo=True)
        ctx.run(f"git add    {work_dir_pth / 'dvc.lock'}",         echo=True)
ns.add_task(_git_hook)



@task(pre=[build_book])
def share(ctx, overwrite=False):
    """
    copy built book to share location
    """
    cur_branch = ctx.run('git rev-parse --abbrev-ref HEAD', hide='out').stdout.replace('\n','')
    cur_hash   = ctx.run('git rev-parse              HEAD', hide='out').stdout.replace('\n','')
    import yaml
    book_shr = Path(yaml.safe_load(open(work_dir_pth / 'config.yml'))['share']['loc'])
    assert(book_shr.exists())
    branch_dst = book_shr / cur_branch
    hash_dst =   book_shr / cur_hash
    book_src = work_dir_pth / 'build' / '_build' / 'html'

    def cpy(dst):
        from shutil import rmtree
        if dst.exists():
            if overwrite:
                print(f'removing existing directory {dst} (overwrite=True)')
                rmtree(dst)
                #from shutil import copytree
                print(f'copying to {dst}')
                copytree(book_src, dst, )
            else:
                print(f'dest {dst} exists (overwrite=False)')
        else:
            print(f'copying to {dst}')
            copytree(book_src, dst, )

    cpy(branch_dst)
    cpy(hash_dst)
    return
ns.add_task(share)


######

import shutil
import os
#http://mathieuturcotte.ca/textes/copytree2/
def copytree(src, dst, symlinks=False, ignore=None, progress=None):
    """
    A nonrecursive reimplementation of shutil.copytree with
    a progress callback based on the number of copied files.
    Works well over large folder trees containing lot of small
    files.

    Tested against the shutil test suite, specifically:
        - test_copytree_simple
        - test_copytree_with_exclude
        - test_copytree_named_pipe

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.

    The optional ignore argument is a callable. If given, it
    is called with the `src` parameter, which is the directory
    being visited by copytree(), and `names` which is the list of
    `src` contents, as returned by os.listdir():

        callable(src, names) -> ignored_names

    Even if this implementation of copytree is not recursive,
    the callable will be called once for each directory that
    is copied. It returns a list of names relative to the `src`
    directory that should not be copied.

    The optional progress argument is a callable. If given, it
    will be called several times during the copytree operation
    with the `over` parameter, which is the total number of files
    to copy, and `done` which is the total number of files already
    copied. You shouldn't take for granted that progress will be
    called for every file copied, but it is assured that it will
    be called when the copytree operation is completed.

        callable(over, done) -> void
    """
    names = [('','')] # start at the root of src

    for name in names:
        # name[0] -> path to name[1], relative to src
        # name[1] -> file or folder currently handled
        relname = os.path.join(name[0], name[1])
        absname = os.path.join(src, relname)

        if os.path.isdir(absname):
            nnames = os.listdir(absname)
            ignored_names = []

            if ignore is not None:
                ignored_list = ignore(absname, nnames)
                for ignored in ignored_list:
                    ignored_names.append((relname, ignored))

            for nname in nnames:
                entry = (relname, nname)
                if entry not in ignored_names:
                    names.append(entry)

    todo = len(names)               # total number of files to copy
    done = 0                        # total number of files copied
    freq = round(todo * 0.01)       # number of files to copy between call to progress
    since = 0                       # number of copied files since last call to progress

    errors = []

    # Before we start, do a fast checkup to make
    # sure that dst doesn't already exists.
    # Anyway, It's the shutil.copytree behavior.
    os.makedirs(dst)
    os.removedirs(dst)
    from tqdm import tqdm
    for name in tqdm(names):
        if name in ignored_names:
            continue

        srcname = os.path.join(src, name[0], name[1]) # abs path to source file
        dstname = os.path.join(dst, name[0], name[1]) # abs path to destination file

        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                os.makedirs(dstname)
            else:
                # Will raise a SpecialFileError for unsupported file types
                shutil.copy2(srcname, dstname)

            if progress is not None:
                done += 1
                since += 1
                if since >= freq:
                    since = 0
                    progress(todo, done)

        # catch the Error so that we can continue with other files
        except shutil.Error as err:
            errors.extend(err.args[0])
        except EnvironmentError as why:
            errors.append((srcname, dstname, str(why)))

    if progress is not None and since != 0:
        progress(todo, done) # we're done

    try:
        shutil.copystat(src, dst)
    except OSError as why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error(errors)
