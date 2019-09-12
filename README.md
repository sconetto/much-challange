# Much APIs

<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

This repository contains the codes for Much's challenge. All code was written in **Python 3.7.3**.

External packages used:

-   [black](https://pypi.org/project/black/) (for code style)
-   [ipdb](https://pypi.org/project/ipdb/) (for debugging)
-   [ipython](https://pypi.org/search/?q=ipython) (for testing)

## 1. Product Group Tree

To execute the first challenge solution, run:

```bash
python3 challenge1.py
```

The `challenge1.py` must be on the same folder level as the JSON with the products (`product_groups.json`).

There is no output, the challenge has a logger that shows the creations being made.

The complexity of the algorithm is O(N²) (Because of the ancestors search).

## 2. Random crashes

To execute the second challenge solution, run:

```bash
python3 challenge2_runner.py
```

Both `challenge2.py` and `challenge2_runner.py` must be on the same folder level as the JSON with the products (`product_groups.json`)

The solution will create two files:

1. `last.bkp`: File with a single integer representing the number of objects saved on the last execution. Located at `/tmp`.

2. `objects.bkp`: File with a list of objects that were saved on the last execution. Located at `/tmp`.

At the final of the execution the `objects.bkp` file must contain a backup of all objects saved during execution.

The complexity of the algorithm is O(N²).

**OBS**: The execution will take a while because of the crashes restart, all file manipulation and loading to memory the backup objects.

## 3. Product Group Tree #2 - Bulk

Work in Progress
