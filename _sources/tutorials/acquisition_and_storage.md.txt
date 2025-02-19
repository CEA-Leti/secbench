---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.6
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Example Side-Channel Acquisition

In this notebook we show how to do an acquisition using the secbench framework, more precisely, the {py:mod}`secbench.api` and {py:mod}`secbench.storage` modules.

## Bench and Hardware Setup

```{code-cell} ipython3
import logging

import matplotlib.pyplot as plt
import numpy as np

from secbench.api import get_bench
from secbench.api.simulation import SimulatedScope
from secbench.storage import Dataset, Store
```

First, we enable the logging and create a {py:class}`Bench`.

```{code-cell} ipython3
logging.basicConfig(level=logging.INFO)
```

```{code-cell} ipython3
bench = get_bench()
```

We now grab a scope.

```{note}
To make the notebook executable without real hardware, we create a simulated scope and register it manually. 
```

```{code-cell} ipython3
scope = SimulatedScope(channel_names=["1", "2"])
bench.register(scope)
```

In a real experiment, the previous cell is not needed, you only need to do:

```{code-cell} ipython3
scope = bench.get_scope()
```

Here we define the parameters of the acquisition:

```{code-cell} ipython3
total_size = 300  # How many traces to acquire.
batch_size = 100   # Size of batches acquisired for segmented acquisition.
n_batches = total_size // batch_size
```

Then, we need to define some device under test (DUT). It is specific to each experiment.
The goal of the device under test is to perform some computation (AES, RSA, ECC or other) and ideally generate a trigger signal.

For this example, we suppose that the DUT processes a 16 byte plaintext. Our implementation bellow will force a trigger on the scope.
In a real side-channel experiment, you will probably need to open a serial port, send the plaintext to the target, etc.

```{code-cell} ipython3
class Dut:
    def process(self, plaintext):
        scope.force_trigger()
```

Now, we instanciate a DUT:

```{code-cell} ipython3
dut = Dut()
```

We generate some inputs for the acquisitions. Rembember that the DUT processes 16-bytes plaintexts in our example.

```{code-cell} ipython3
pts = np.random.randint(0, 256, size=(total_size, 16), dtype=np.uint8)
```

## Dataset Initialization

Now, we can create a {py:class}`~secbench.storage.Store` and a {py:class}`~secbench.storage.Dataset` inside it for our acquisition.
If we were to do multiple acquisition, we could create multiple {py:class}`~secbench.storage.Dataset` with different names.

```{code-cell} ipython3
store = Store('example_campaign.hdf5', mode='w')
```

```{code-cell} ipython3
ds = store.create_dataset('my_acquisition', total_size, 'data', 'pts')
```

## Acquisition

+++

For doing an acquisition, we should first setup the scope and configure the trigger. This can be done manually or via the {py:class}`~secbench.api.instrument.Scope` API. We have a whole tutorial dedicated on this topic in {ref}`sec:using_scopes`.

Here is an example configuration. Do not forget to **update it** if you do a real experiment.

```{code-cell} ipython3
scope["1"].setup(range=3, offset=0)
scope["2"].setup(range=10e-3, offset=0)
scope.set_horizontal(samples=200, interval=1e-8)
scope.set_trigger(channel="1", level=1.2)
```

A good practice is to dump the scope configuration and save it in the dataset.

This is how you get the scope configuration (we only query channels we use in our acquisition):

```{code-cell} ipython3
scope_config = scope.config(channels=["1", "2"])
scope_config
```

This is how you save the scope configuration in a dataset. By convention, we call the asset "scope_config.json".

```{code-cell} ipython3
ds.add_json_asset("scope_config.json", scope_config)
```

If you scope support it, segmented acquisitions can drastically speed-up the acquisition process.

```{code-cell} ipython3
scope.segmented_acquisition(batch_size)
```

Now let's get some traces! Here is a generic acquisition loop:

```{code-cell} ipython3
for batch_number in range(n_batches):
    # We retrieve 10 batches of 100 traces each
    start, end = batch_number * batch_size, (batch_number + 1) * batch_size
    scope.arm()
    for exec_number in range(start, end):
        dut.process(pts[exec_number])
    scope.wait()
    # Query traces from the scope.
    traces, = scope.get_data("1")
    # Add the batch of traces and pts to the dataset.
    ds.extend(traces, pts[start:end])
```

```{code-cell} ipython3
del ds
store.close()
del store
```

## Reloading the Dataset

This section shows how to reload the dataset. First, it is a good idea to inspect the data using the `secbench-db status` command. We can see for the "my_acquisition" dataset, we have `size=300`, which means the dataset was fully populated.

```{code-cell} ipython3
!secbench-db status example_campaign.hdf5
```

Now, we open the store in read-only mode. For analysis, we have no reason to open the store in write mode.

```{code-cell} ipython3
store_reload = Store("example_campaign.hdf5", mode="r")
```

```{code-cell} ipython3
ds = store_reload["my_acquisition"]
```

```{code-cell} ipython3
ds_data = ds["data"]
ds_pts = ds["pts"]
```

When you reload data as show in the previous cell, the data returned **are not numpy arrays**. At this point the data are not loaded in RAM, which is a good thing when you have huge datasets.

```{code-cell} ipython3
print(type(ds_data))
```

Luckily, the `ds_data` and `ds_pts` support almost all numpy array methods.

```{code-cell} ipython3
print(ds_data.dtype)
print(ds_data.shape)
```

```{code-cell} ipython3
ds_data_dram = ds_data[:]
ds_pts_dram = ds_pts[:]
```

```{code-cell} ipython3
print(type(ds_data_dram))
```

At this point, you can do all side-channel processing you want. Our simulated data are not very interesting, but we can plot the mean trace for example:

```{code-cell} ipython3
plt.plot(np.mean(ds_data, axis=0))
plt.xlabel("Sample Index")
plt.ylabel("ADC Sample Value")
plt.show()
```

You can also recover the configuration from the scope:

```{code-cell} ipython3
ds_scope_config = ds.get_json_asset("scope_config.json")
```

```{code-cell} ipython3
ds_scope_config
```

One nice thing is that we can recompute the real time scale of traces.

```{code-cell} ipython3
time_ns = 1e9 * scope_config["scope_horizontal_interval"] * np.arange(ds_data.shape[1])

plt.plot(time_ns, np.mean(ds_data, axis=0))
plt.xlabel("Time (ns)")
plt.ylabel("ADC Sample Value")
plt.show()
```
