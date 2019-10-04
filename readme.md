This repository represents a 'workspace' for both code (both 'library' type code and scripts) _and_ data (non-code generally).
* **Code**, representing fuctionality, configuration, and data _pointers_ is managed by `git`.
* **Data** are (the word 'data' is plural, ok?) managed by `dvc` ([data science version control](http://dvc.org)).
* **Environments** are managed by [`conda`](https://docs.conda.io) and [`conda devenv`](https://conda-devenv.readthedocs.io).
* **Tasks** are mangaged by [`invoke`](http://docs.pyinvoke.org).

# Development Environment Setup


0. **_Base_ Tools** 

    Follow [instructions](dev-bootstrap/readme.md) for an automated installation of _base_ development tools.

1. **Code Repository**

    Enter 'base' environment: `conda activate base`.
    Then obtain source with
    `> git clone https://stash.pnnl.gov/scm/usarml/workspace-code.git workspace`.
    <br>
    The source was cloned into the 'workspace' directory even though it's called 'workspace-code' to emphasize that code and non-code will combine in the directory.

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

    Go through the setup tasks given by `> inv -l`.
    Generally, if no error shows up, the task can be considered successful.

    DVC

    One of these tasks is to set the DVC remote repo.
    This repo is on the shared drive at \\\pnl\projects\ArmyReserve\ESTCP\Machine Learning\software-files\dont-touch\not-code-dvc-repo, so check that you can access it.
    Optionally, make this folder available offline for better performance (Windows feature). <br>
    > Do not modify this directory (yourself)!

    The DVC setup task should inform you of a downloaded sample dataset.

    MDMS

    Get access in order to complete the MDMS setup task.


# Workflow


Manage source code with `git` (as usual), but also use `dvc` to manage data and generated assets such as notebooks, intermediate files (dvc pipelines), documentation, visualizations, and model files.
This separation is enforced with a restrictive [.gitignore](.gitignore).
Installing [DVC git hooks](https://dvc.org/doc/commands-reference/install) helps to automate this.



<!--
work dirs flat
branching? base env and libs 
use isse tracker on bitbucket?
1. Create
1. create folder. keep it flat. unit of work.
create a branch. data-demo suggested example.
-->
