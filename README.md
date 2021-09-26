# Streamlet

This is a short description of the Streamlet project.

## Local setup

Below you will find a list of tools used for local setup.

**Docker**. We use *docker-compose* to set up containers. Install *Docker* following the instructions on the *Docker* [website](https://docs.docker.com/compose/install/).

**Pipreqs**. Auto-generate the requirements file for the project based on actual imports, not on installed packages. Install with `pip install pipreqs`.

**Requirements from containers**. For IDEs without *Docker* debug capabilities (e.g. *PyCharm CE*), requirements can be satisfied by running `pip install -r requirements.txt`.

**Pre-commit.** Perform pre-commit code reformatting and checks. Install with `pip install pre-commit`. A full list of pre-commit hooks is specified in the `.pre-commit-config.yaml` file. In particular, we use:

- *Mypy* for static type checking.
- *isort* for grouping and sorting imports.
- *Black* for code formatting.
- *flake8* for non-style checks.

**pytest**. Handle tests. Can be installed via `pip install pytest`. Tests are not included in pre-commit hooks and should be run manually.
