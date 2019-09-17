This repository represents a 'workspace' for both code _and_ data (non-code generally). Code is managed by `git` while data is managed by `dvc` ([data science version control](http://dvc.org)).


# Setting up workflow

1. Access Git Code repo

    `git clone https://stash.pnnl.gov/scm/usarml/workspace-code.git workspace`
    <br>
    Cloned into 'workspace' folder even though it's called 'workspace-code' to emphasize that code and non-code will combine in the directory.

2. Access DVC non-code repo

    This repo is on the shared drive \\\pnl\projects\ArmyReserve\ESTCP\Machine Learning\software-files\dont-touch\not-code-dvc-repo, so check that you can access it.

    Do not modify this directory (yourself)!

3. DVC

    1. [Install `dvc`](https://dvc.org/doc/get-started/install).

    2. Set the DVC remote (in [.dvc/config](.dvc/config)). A Windows example is hardcoded so change accordingly with `dvc remote modify url <location>`.
    <br>
    On Windows, map \\\pnl\projects to a drive. So the DVC repo would be E:\ArmyReserve\ESTCP\Machine Learning\software-files\dont-touch\not-code-dvc-repo


 Try `dvc` by downloading [sample data](data/sample.dvc): `dvc pull data/sample.dvc`   .


# Workflow

Manage source code with `git` (as usual), but also use `dvc` to manage data and generated assets such as notebooks, intermediate files (dvc pipelines), documentation, visualizations, and model files. This separation is enforced with a restrictive [.gitignore](.gitignore). Installing [DVC git hooks](https://dvc.org/doc/commands-reference/install) helps to automate this.


<!-- branching? base env -->
