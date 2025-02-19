---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.0
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

```{py:module} secbench.storage
  :no-index:
```



(sec:secbench-storage-walkthrough)=

# Secbench Storage

```{only} builder_html
  You can also open this tutorial in a secbench environment {download}`download the notebook <./storage_walkthrough.md>` and open it in a Jupyter in the secbench environment.
```

## Overview

The secbench storage API is a *thin* layer on top of HDF5 files (see [h5py Documentation](https://docs.h5py.org/en/stable/index.html)).

It provides a {py:class}`~Store` class, which abstracts the storage backend, such as a HDF5 file. A store contains zero or more {py:class}`~Dataset`. 

A {py:class}`~Dataset` object represents an aggregation of several measurements. You can think of a dataset as a 2-dimensional array, where each row contains different fields (for example, `x`, `y`, `z`, `temperature`).

In side-channel analysis, we usually create a dataset for each acquisition campaign, with fields like:
- side-channel measurements from the scope,
- the plaintext associated with each trace,
- the ciphertext associated with each trace.

In this walkthrough, we will see how to create a dataset and read it. 

We start with some imports.

```{code-cell} ipython3
import json

# All data are represented and stored as numpy arrays
import numpy as np

# Dataset
from secbench.storage import Dataset, Store
```

## Creating Datasets

The tutorial uses generated data, so that the notebook is self-contained. 

We generate a 50MB dataset. This is not sufficient to get a taste of the performances achieved by the library. But, feel free to adapt the parameters to fit on your machine.

```{code-cell} ipython3
capacity = 10_000
samples = 5_000
```

```{code-cell} ipython3
data = np.random.randint(-128, 127, size=(capacity, samples), dtype=np.int8)
pts = np.random.randint(0, 256, size=(capacity, 16), dtype=np.uint8)
```

```{code-cell} ipython3
print(f'Dataset size: {data.size / 1e6} Mb')
```

The first step before creating or loading some dataset is to open a destination {py:class}`~Store`. For this, we use the {py:meth}`secbench.storage.Store.open` class method.

We create one called "walkthrough.hdf5". 

Note that we open this file in 'w' mode, which clears the file at each execution. This mode is convenient for the tutorial. However, in practice, **we recommend the 'a' mode when writing** a dataset and the **'r' mode when reading** a dataset. The modes supported by {py:meth}`secbench.storage.Store.__init__` constructor are:

| Mode (string) | Mode (OpenMode)              | Description |
|---------------|------------------------------|-------------|
| 'r'           | `OpenMode.read`              | Read only, file must exist (default) |
| 'r+'          | `OpenMode.read_write`        | Read/write, file must exist |
| 'w'           | `OpenMode.create_truncate`   | Create file, truncate if exists |
| 'w-'          | `OpenMode.create`            | Create file, fail if exists |
| 'a'           | `OpenMode.read_write_create` | Read/write if exists, create otherwise |

```{code-cell} ipython3
store = Store('walkthrough.hdf5', mode='w')
```

Now, we can create a dataset called "my_acquisition" (the name should be chosen to easily identify datasets). This dataset will have a capacity of ``100_000`` entries and two fields: "data" and "plaintext". 

It means that this dataset can hold at most `100_000` pairs of "data" and "plaintext". When created, the dataset is empty.

```{code-cell} ipython3
ds = store.create_dataset('my_acquisition', capacity, 'data', 'plaintext')
```

We can introspect various information about the dataset. The ``size`` attributes represent the number of rows in the dataset.

```{code-cell} ipython3
print("fields:", ds.fields())
print("capacity:", ds.capacity)
print("size", ds.size)
```

The first way to add some entries in the dataset is to use the {py:meth}`secbench.storage.Dataset.append` method, which adds a single entry.

```{code-cell} ipython3
%%time
for i in range(1000):
    ds.append(data[i], pts[i])
```

We can see that the size of the dataset was updated.

```{code-cell} ipython3
print(ds.size)
```

However, a much **faster way to insert traces**  (20x faster!) is to use the {py:meth}`~Dataset.extend`, which add many entries at once.

```{code-cell} ipython3
%%time
ds.extend(data[1000:2000], pts[1000:2000])
```

**IMPORTANT**: On the first call to {py:meth}`~Dataset.extend` or {py:meth}`~Dataset.append`, those methods look at the type and shape of all fields (here `data`, and `pts`) and allocate the data in the HDF5 file. This implies that **the arguments to `append` (or `extend`) must always have the same type and shape**. 

Once there are some rows added in the dataset, you can access directly the underlying arrays with the {py:meth}`~Dataset.get` method. This method return the array with its full capacity, the data is only valid on the slice `[:ds.size]`.

```{code-cell} ipython3
ds_data, ds_plaintext = ds.get('data', 'plaintext')
print(ds_data[0])
print(data[0])

print(ds_data.shape)
```

If something went wrong, you can reset the dataset and reinstert data.

```{code-cell} ipython3
print('size (before reset)', ds.size)
ds.reset()
print('size (after reset)', ds.size)
```

Now, we store the full dataset in one shot. HDF5 uses buffering, storing 50MB is instant but inserting gigabytes is also very fast!

```{code-cell} ipython3
%%time
ds.extend(data, pts)
```

### Adding Assets

It is very frequent to add constant data in a dataset (e.g., the secret key used, the scope configuration).
You can add an assets (a numpy array or raw bytes as follows). You will do that with three methods:
- {py:meth}`~Dataset.add_asset`, to insert or replace an asset,
- {py:meth}`~Dataset.get_asset`, to retrieve the content of the assets,
- {py:meth}`~Dataset.assets`, to list assets available.

In addition, we provide two helpers:
- {py:meth}`~Dataset.add_json_asset`: encode a python object in JSON format and store it as an asset
- {py:meth}`~Dataset.get_json_asset`: load an asset stored in JSON format.

```{code-cell} ipython3
ds_2 = store.create_dataset("dataset_with_assets", 10, "x", "y")
```

```{code-cell} ipython3
ds_2.append(np.array([1, 2]), np.array([3, 5]))
```

Let insert some assets:

```{code-cell} ipython3
ds_2.add_asset("name_of_the_asset", np.arange(100, dtype=np.int16))
ds_2.add_asset("name_of_byte_asset", b"coucou")


scope_config = {"samples": 100, "precision": 1e-3}
ds_2.add_json_asset("scope_config.json", scope_config)
```

```{note}
Here, we crafted a dummy scope config manually. In a real acquisition, you may find the {py:meth}`secbench.api.instrument.Scope.config` method helpful to obtain this JSON object.
```

Now, we can see that the assets are present in the dataset and try to load them.

```{code-cell} ipython3
ds_2.assets()
```

```{code-cell} ipython3
ds_2.get_asset("name_of_the_asset")
```

```{code-cell} ipython3
ds_2.get_json_asset("scope_config.json")
```

### Exercice

It is time for you to dive in!

- (1) Create a dataset named "exercice_1", with 4 fields "x", "y", "z", "power", with a capacity of 300 elements.
- (2) Add a single entry into it. We assume that "x", "y" and "z" have type `np.float32`.
    
    - (a) Try something like ``ds_ex.append(3.0, 4.5, 5.0, power)``, why does it fails? 
    - (b) To fix this issue, try to pass explicitely typed scalar values: ``np.float32(3.0)`` instead of ``3.0``.
- (3) Fill the rest of the dataset with `extend`.
- (4) Try to add an additional entry and see what happens
- (5) add an asset in the dataset

```{code-cell} ipython3
:tags: [hide-input]

# Solution to (1) 
ds_ex = store.create_dataset('exercice_1', 1000, 'x', 'y', 'z', 'power')
print(ds_ex.fields())
```

```{code-cell} ipython3
:tags: [hide-input]

# Solution to (2)
try:
    ds_ex.append(3.0, 4.5, 5.0, np.random.random(10))
except AttributeError as e:
    print("!! append raised an exception:", e)
# (2.a) It fails because the values are not explicitely typed.

# (2.b) correct call:
ds_ex.append(np.float32(3.0), np.float32(4.5), np.float32(5.0), np.random.random(10))
print("ds_ex, size after insertion:", ds_ex.size)
```

```{code-cell} ipython3
:tags: [hide-input]

# Solution to (3)
coords = np.random.random(1000 - 1).astype(np.float32)
power = np.random.random(size=(1000 - 1, 10))

ds_ex.extend(coords, coords, coords, power)
```

```{code-cell} ipython3
:tags: [hide-input]

# Solution to (4)
try:
    ds_ex.append(np.float32(3.0), np.float32(4.5), np.float32(5.0), np.random.random(10))
except ValueError as e:
    print("!! append raised an exception:", e)
```

```{code-cell} ipython3
:tags: [hide-input]

# Solution to (5)
ds_ex.add_asset("demo_asset", b"anything you want")
```

For continuing the tutorial, we close the HDF5 file used for creating the dataset.

```{code-cell} ipython3
store.close()
del store
```

## Loading Datasets

When working in analysis phases, we recommend to **open HDF files in read-only mode** to prevent unexpected modifications.

```{code-cell} ipython3
store = Store.open('walkthrough.hdf5', mode='r')
```

You can look at datasets available with the {py:class}`~Dataset.datasets` method.

```{code-cell} ipython3
list(store.datasets())
```

You can also check if a dataset is available, or iterate the name of datasets:

```{code-cell} ipython3
print("'my_acquisition' defined:", "my_acquisition" in store)
print("'not_existing' defined:", "not_existing" in store)

print("\nDatasets:")
for name in store:
    print("-", name)
```

Then, you can open the dataset with {py:meth}`~Store.load_dataset` or using the `store["dataset_name"]` syntax, as follows:

```{code-cell} ipython3
ds_rd = store["my_acquisition"]
print("size:", ds_rd.size, "/", ds_rd.capacity)
```

You can then access the fields using the `get` method (or using the `dataset["field name"]`syntax):

```{code-cell} ipython3
data_rd = ds_rd["data"]
print(data_rd[0])
print(data[0])
```

In addition, you can easily check if a field is available or iterate field names:

```{code-cell} ipython3
print("'data' field exists:", "data" in ds_rd)
print("'aa' field exists:", "aa" in ds_rd)

print("\nFields:")
for name in ds_rd:
    print("-", name)
```

If you opened the file in read/write (e.g., 'a' mode), you can continue to push rows in the dataset or reset it. But it read-only mode, those operations will fail.

```{code-cell} ipython3
try:
    ds_rd.reset()
    ds_rd.append(data[0], pts[0])
except Exception as e:
    print("!! got runtime error:", e)
```

## Command Line Interface

The command line tool `secbench-db` allows direct interaction with a dataset.

### Exporting a Dataset

+++

You can export datasets from the command line, or using the {py:meth}`~Store.export` method.

```{code-cell} ipython3
!secbench-db status walkthrough.hdf5
```

```{code-cell} ipython3
!rm -f walkthrough_export.hdf5
```

```{code-cell} ipython3
!secbench-db export -o walkthrough_export.hdf5 --rename exercice_1_exp walkthrough.hdf5 exercice_1
```

```{code-cell} ipython3
!secbench-db status walkthrough_export.hdf5
```

### Cleanup

```{code-cell} ipython3
!rm -f walkthrough walkthrough_export.hdf5
```
