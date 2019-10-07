# I. Workflow

This repository represents a 'workspace' for both source code (both 'library' type code and scripts, referred to as just 'code' from here on) _and_ non- source code (data and generated assets, referred to as just 'files' from here on).
In addition, execution environments and workflow tasks are managed as well.

* **Code**, representing fuctionality, configuration, and file _references_ is managed by `git`.
* **Files** are managed by `dvc` ([data science version control](http://dvc.org)).
* **Environments** are managed by [`conda`](https://docs.conda.io) and [`conda devenv`](https://conda-devenv.readthedocs.io).
* **Tasks** are mangaged by [`invoke`](http://docs.pyinvoke.org).

## Structure

To keep things as simple as possible, 'work directories' (workdir) are the folders directly under the root of the workspace.
In other words, the workdir structure is flat so the collaborator can immediately identify units of work.
Nonetheless, each workdir can have its own directory hierarchy.

A workdir has 'development' and 'run' environment requirements (in separate files).
Development requirements include run requirements in addition to tools that aid the development process such as code linters and test frameworks (that are not needed to just use what's in the workdir).
Also, the requirements can include the requirements of other workdirs.
So, a workdir represents a unit of work that is separated out, but can depend on other workdirs.
For example, in this repository, the 'data-demo' workdir has the run requirements of 'data-interface' _in addition to_ requirements to create visualizations (that are not needed to just use the the interface).

## Process

The structure is formalized by the tasks that are defined in `invoke`.
The tasks (try to) align code, files, and execution environments.
The tasks aid the following development process.

1. Initialize workdir.

    Initializing a workdir is accomplished by invoking the `work-on` task: `> invoke work-on <workdirname>`.
    Then, declare dependencies by modifying the environment.devenv.yml and environment.run.yml files (in the created directory).

    Before initilizing the workdir however, it is recommended to work on a separate git branch to 'freeze' the workdir dependencies.
    All workdirs will depend on at least a baseline of work units (will almost always be at least the 'data-interface')
    but the functionality of the dependencies will change.

2. Develop with git source control.

    Manage (source) code (only) with `git` and keep data and generated assets such as notebooks, intermediate files, documentation, visualizations, and model files out of source control.
    This separation is enforced with a restrictive [.gitignore](.gitignore);
    All files are ignored except patterns that are considered (source) code.

    `dvc run` is useful here to declare an execution consisting of input files, commands, and output files.
    Use `> dvc pull <dvcfile>` to obtain file dependencies.

    It may be useful to, again, create a branch to represent different versions of the work.

3. Reproduce.

    Reproduction of an execution is achieved when input files, commands, and the execution environment are specified.
    Through a .dvc file, `dvc repro` manages input files and commands (but not the execution environment directly).
    Now, the environment.*.yml files should reflect the development environment.
    So the way to ensure reproduction of the execution is to take the following steps:
    1. `> conda remove estcp-<workdir>`
    2. `> conda devenv` (in the workdir)
    3. `> dvc repro <dvcfile>`.

4. Commit.

    The usual `git commit` command has been modified to prepend the commit message with '[workdir]' to help identify top-level work.
    This prefix is taken from the development environment name (not the current directory).

    After committing code, representing functionality and an execution process, generated assets should be shared with a `dvc push`.
    Installing [DVC git hooks](https://dvc.org/doc/commands-reference/install) helps to automate following a `git push` with a `dvc push`.



# II. Development Environment Setup


0. **_Base_ Tools** 

    Follow [instructions](dev-bootstrap/readme.md) for an automated installation of _base_ development tools.

1. **Code Repository**

    Enter 'base' environment: `> conda activate base`.
    Then obtain source with
    `> git clone https://stash.pnnl.gov/scm/usarml/workspace-code.git workspace`.
    <br>
    The source was cloned into the 'workspace' directory even though it's called 'workspace-code' to emphasize that code and non-code will combine in the directory (see Workflow section below).

2. **Project Tools**

    After that, from the 'project' directory, install [project-specific tools](project/environment.run.yml) into a _project_ base environment with:
    `> conda devenv`.

    After entering the development environment, with `> conda activate estcp-project`, check that you can list development [tasks](project/estcp_project/tasks/tasks.py) with: `> inv -l`. 
    <br>
    Use `-h` before the task name to learn about the task like:
    ```
    (estcp-project) > inv -h list-work-dirs
    Usage: inv[oke] [--core-opts] list-work-dirs [other tasks here ...]

    Docstring:
    Lists work directories

    Options:
    none
    ```

3. **Configure**

    Go through the setup tasks given by `> inv -l setup` with `> inv setup`.
    Generally, if no error shows up, the task can be considered successful.

    * DVC

        One of these tasks is to set the DVC remote repo.
        This repo is on the shared drive at \\\pnl\projects\ArmyReserve\ESTCP\Machine Learning\software-files\dont-touch\not-code-dvc-repo, so check that you can access it.
        Optionally, make this folder available offline for better performance (Windows feature). <br>
        > Do not modify this directory (yourself)!

        The DVC setup task should inform you of a downloaded sample dataset.

    * MDMS

        Get access in order to complete the MDMS setup task.


<!--
use isse tracker on bitbucket?
-->
