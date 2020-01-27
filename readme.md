# I. Workflow

This repository represents a 'workspace' for both source code (both 'library' type code and scripts, referred to as just 'code' from here on) _and_ non- source code (data and generated assets, referred to as just 'files' from here on).
In addition, execution environments and workflow tasks are managed as well.

* **Code**, representing fuctionality, configuration, and file _references_ is managed by `git`.
* **Files** are managed by `dvc` ([data science version control](http://dvc.org)).
* **Environments** are managed by [`conda`](https://docs.conda.io) and [`conda devenv`](https://conda-devenv.readthedocs.io).
* **Tasks** are managed by [`invoke`](http://docs.pyinvoke.org).

## Structure

The workflow manages a 'work directory' (workdir) concept: some separated-out unit of work.
It could be a module/library or a one-off experiment.
To keep things as simple as possible, workdirs are the folders directly under the root of the workspace.
The workdir structure is flat so collaborators can immediately identify units of work.
Nonetheless, each workdir can have its own directory hierarchy obviously.

A workdir has 'development' and 'run' environment requirements (in separate files).
Development requirements typically include the run requirements in addition to tools that aid the development process such as code linters and test frameworks (that are not needed to just use what's in the workdir in a derivative work).
To achieve this, each environment file has an 'includes' and 'dependencies' section.
The 'includes' include other environment files (in other workdirs) while the 'dependencies' refer to published packages.
So, the 'includes' section in the environment files can be thought of as 'internal' dependencies
while the 'dependencies' section can be thought of as 'external' dependencies.
However, as mentioned previously, run requirements shouldn't 'include' dev requirements.

All workdirs will depend on a baseline of (internal) workdirs (which, in turn, have a set of external dependencies).
Also the work directory path will be appended to the PYTHONPATH environment variable in the run environment by default.
This makes Python packages in the directory visible to workdirs that depend on it.

So, a workdir represents a unit of work that is separated out, but can depend/build on other workdirs.
See the [workflow-demo](./workflow-demo/readme.md) (in the workflow-branch).

## Process

The workflow is formalized by the tasks that are defined in `invoke`.
The tasks (try to) align code, files, and execution environments.
The tasks aid the following development process.

1. Initialize and resume work in work directories.

    The `work-on` task (`> invoke work-on <workdirname>`) is intended to be an entry point into work by partially automating the following process.
    Tasks that are not automated can be completed by following instructions when prompted.

    0. Initialization of
    
        *Directory contents.*
        A work directory (with environment files) will be created if one does not exist.

        *Source control.*
        After that, the newly created files will be committed to source as an initial `git` commit on the current branch (most likely the 'master' branch).
        However, after the initial commit, it is recommended to work on a separate git branch to 'freeze' the workdir code dependencies as they will by subject to change.
        
        *Environment.*
        Declare the dependencies by modifying the environment.devenv.yml and environment.run.yml files (in the created directory).
        See conda [devenv documentation](https://conda-devenv.readthedocs.io/en/latest/).

    1. Environment check

        Once a workdir has been initialized, the task will instruct to switch to the workdir environment and directory.

2. Manage source and file references.

    Manage (source) code (only) with `git` and keep data and generated assets such as notebooks, intermediate files, documentation, visualizations, and model files out of source control.
    This separation is enforced with a restrictive [.gitignore](.gitignore);
    All files are ignored except patterns that are considered (source) code.

    `dvc run` is useful here to declare an execution consisting of input files, commands, and output files which will generate a .dvc file to be source controlled.
    Use `> dvc pull <dvcfile>` to obtain input files.

    It may be useful to, again, create a branch to represent different versions of the work.

3. Reproduce.

    Reproduction of an execution is achieved when input files, commands, and the execution environment are specified.
    Through a .dvc file, `dvc repro` manages input files and commands (but not the execution environment directly).
    Now, the environment.*.yml files should reflect the development environment.
    So the way to ensure reproduction of the execution is to recreate the development environment as follows:
    1. `> inv remove-work-env --work-dir <workdir>`
    2. `> dvc repro <dvcfile>`.

4. Commit source and files.

    The usual `git commit` command has been modified to prepend the commit message with '[workdir]' to help identify top-level work.
    This prefix is taken from the development environment name (not the current directory).

    After committing code, representing functionality and an execution process, generated assets should be shared with a `dvc push`.
    Installing [DVC git hooks](https://dvc.org/doc/commands-reference/install) helps to automate following a `git push` with a `dvc push`.
    However, in this project, the hooks are installed by default.
    If not, `inv setup.create-dvc-git-hooks`.

See [worflow-demo](https://stash.pnnl.gov/projects/USARML/repos/workspace-code/browse/workflow-demo/readme.md?at=workflow-demo). 

# II. Development Environment Setup


0. **_Base_ Tools** 

    Follow [instructions](dev-bootstrap/readme.md) for an automated installation of _base_ development tools.

1. **Code Repository**

    Enter 'base' environment: `> conda activate base`.
    Then obtain source with
    `> git clone https://stash.pnnl.gov/scm/usarml/workspace-code.git workspace`.
    <br>
    The source was cloned into the 'workspace' directory even though it's called 'workspace-code' to emphasize that code and non-code will combine in the directory (see Workflow section above).

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

    * ~~MDMS~~

        ~~Get access in order to complete the MDMS setup task.~~


# III. Architecture


The trunk (master branch) contains baseline/common assets (code, data files).
They can be organized as a 'stack' where top layers build on lower layers.


* Layer 0: Workflow tools

    source code mgt.: `git` is the fundamental 'entry point' into the workspace.
    This is closely followed by `dvc` as they work together.


* Layer 1: (Raw) data files

    Mainly MDMS files, EBCS files, and meta data.
    These are stored in /data.

* Layer 2: 'Data interface'

    Metadata database: Structures relationships in the raw data and exposes the relationships as a Python-based object relational map (ORM).

* Layer 3: 'API'

    The API is differentiated from the 'data interface' since it hides 'raw' data connections that are not of interest to an analyst.
    Instead, the API is concerned with presenting a meaningful querying interface to the analyst.

* Layer 4: Analysis

    Examples of analyst-generated assets: visualizations, models, and documents.
    They may be stored as (non- source code) files managed by DVC.

* Layer 5: Applications

    Applications are essentially a manifestation of use cases.
    For example, an user interface could be presented to identify potential equipment faults.

Generally, lower layers are firmer than upper layers.
For example, data are expected to be relatively fixed.
However, the API can change according to need.


<!--
use isse tracker on bitbucket?
-->
