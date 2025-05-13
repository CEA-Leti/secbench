(sec:installation)=

# Installation

For users that want to use *Secbench* in their project, the *Secbench* Python
packages can be installed through `pip`:

```console
$ pip install secbench-api secbench-storage secbench-picoscope secbench-native secbench-processing
```

You can install packages individually if you do not need all modules.

The minimum Python version supported is 3.10 (some packages may work on older Python versions, but are not tested anymore).

```{note}
*Secbench* is mainly used on Linux. However, since the packages are
pure-Python, they should work on other OSes.
```

If you plan to use Picoscope oscilloscope, they are some additional setup to be
performed, as explained in {py:mod}`secbench.picoscope` module documentation.

## Developers

### Secbench SDK installation

For people that want to develop *Secbench*, build the documentation or try the
example notebooks, we have a script (for Linux) that creates a Python virtual
environment using [miniforge](https://github.com/conda-forge/miniforge), and
install all packages in development mode and some extra dependencies.
This installation method has little pre-requisites and should work out of the box.

First, clone the repository:

```console
$ git clone https://github.com/CEA-Leti/secbench.git
```

Run the installation script.

```{warning}
The following command-line will install the Secbench SDK in the directory `~/tools/secbench_sdk`.
Feel free to use another directory on your computer (it will be created if the directory does not exists).
```

```console
$ ./sdk/setup.sh -p ~/tools/secbench_sdk
```

```{note}
It is safe to re-run the previous command line, it will update packages.
```

Then, you will need to activate the environment to set the environment variables:
```console
source ~/tools/secbench_sdk/activate
```

### Installation in a Python virtual environment

It is also possible to install packages in development mode in an existing Python
[virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#create-and-use-virtual-environments).

If you do not have a virtual environment, create it (here we use the directory `.venv`, feel free to change it):

```console
$ python3 -m venv .venv
$ ./.venv/bin/pip install --upgrade pip
```

To install Secbench packages in the environment, simply run:

```console
$ pip install -e ./src/secbench-api -e ./src/secbench-storage -e ./src/secbench-picoscope -e ./src/secbench-processing -e ./src/secbench-native
```
