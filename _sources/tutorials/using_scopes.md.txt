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

(sec:using_scopes)=

# Using Scopes

This tutorial describes the {py:class}`~secbench.api.instrument.Scope` interface provided by secbench to manage scopes.

+++

In the most common setups, the acquisition flow will look like this:

```{eval-rst}
.. graphviz::

   digraph G {
      rankdir = LR;
      {rank=same; setup}
      {rank=same; stop}
      {rank=same; acquire}
      setup -> acquire -> stop;
      acquire -> acquire;
      stop [label="Exit"];
      setup [label="Initial setup"];
      acquire [label="Acquire batch"];
   }
```
Start by retrieving a scope instance from a {py:class}`~secbench.api.Bench` (see {ref}`sec:secbench-essential-concepts`). In a normal script (or notebook), you would simply do:

```python
from secbench.api import get_bench

bench = get_bench()
# instantiate a scope
scope = bench.get_scope()
```

For this tutorial, we will use the class {py:class}`~secbench.api.simulation.SimulatedScope`, which, as its name suggests simulates a scope. 

First we enable logging:

```{code-cell} ipython3
import logging

logging.basicConfig(level=logging.INFO)
```

Then we create the bench and load the {py:class}`~secbench.api.simulation.SimulatedScope`.

```{code-cell} ipython3
from secbench.api import get_bench
from secbench.api.enums import Arithmetic, Coupling, Decimation, Slope

from secbench.api.simulation import SimulatedScope
```

```{code-cell} ipython3
bench = get_bench()
```

```{code-cell} ipython3
# Force the Simulated scope to be used instead of a real scope.
scope = SimulatedScope(["1", "2", "3"])
bench.register(scope)
```

Now, if we request a scope, we should obtain our scope simulator.

```{code-cell} ipython3
scope = bench.get_scope()
print(scope)
```

## Device Configuration

### Manual setup using the scope knobs & buttons

For side-channel experiments, we recommend tuning the scope parameters manually through knobs and buttons, it will save you a ton of time compared to configuring through the Python API.
Once your setup is good, you can save it on the scope.

Unless you want to learn how to configure the scope using secbench API, you can
skip {ref}`sec:scope-setup` and jump directly to {ref}`sec:scope-trigger`.  Otherwise,
sit tight.

+++

### Setup using device presets

If you are satisfied with your manual setup of the instrument, and the
instrument supports saving the settings to a file, you can save such a preset
using the scope interface and then load it from the Python API.

For example, say you have saved a preset called `experience-1.dfl` (don't
mind the extension, it is vendor-specific) in the scope's default preset
folder. You can then use
{py:meth}`~secbench.api.instrument.HasSetupStorage.setup_load` to load this file:

```python
scope.setup_load('experience-1.dfl')
```

to load the settings before starting your acquisitions. You may also use an
absolute path, eg. `C:\Users\experience-1.dfl` but don't forget to use the
`r`-string syntax to escape the `\` characters of the Windows path:

```python
scope.setup_load(r'C:\Users\experience-1.dfl')
#                ^ note the r
```

You can also save a preset on the device using
{meth}`~secbench.scope.Scope.setup_save`:

```python
scope.setup_save('experience-2.dfl')
```

+++

(sec:scope-setup)=

### Setup using secbench

When setting up the scope using the API, it is a good idea to first perform a
device reset, so you get a clean state to work with:

```{code-cell} ipython3
# reset to factory defaults
scope.reset()
```

You can then enable one or multiple channels and configure their vertical parameters:

```{code-cell} ipython3
# list available channels
print(scope.channel_names())
```

To set channel "1" with a range of 2 V, offset of -1 mV, DC coupling:

```{code-cell} ipython3
scope["1"].setup(range=2, offset=-1e-3, coupling=Coupling.dc)
```

You may omit some parameters to {py:meth}`secbench.api.instrument.ScopeAnalogChannel.setup`, only the parameters passed will be updated. For example to change the vertical range to 1V:

```{code-cell} ipython3
scope["1"].setup(range=1)
print(f"range =", scope["1"].range(), "Volts")
```

```{note}
If you provide values that the scope is unable to honor (eg. unsupported
range or offset), an {exc}`~secbench.api.exceptions.InvalidChannelSetupError` will be
raised.
```

+++

The default decimation method (ADC to data stream resampling) is a basic downsampling method. On supported hardware you can use other methods, such as peak detect, by passing an additional {attr}`decimation` parameter:

```{code-cell} ipython3
# peak detect decimation method
scope["1"].setup(range=2, coupling=Coupling.dc, decimation=Decimation.peak)
```

Then, the horizontal setup can be achieved using any combination of:

- acquisition duration
- number of samples
- duration per sample

For instance:

```{code-cell} ipython3
# 20M samples, during 1 second
scope.set_horizontal(samples=20e6, duration=1)

# 5k samples, with 1 sample = 1µs
scope.set_horizontal(samples=5e3, interval=1e-6)

# 1 sample = 1µs, during 5 seconds
scope.set_horizontal(interval=1e-6, duration=5)
```

```{note}
The scope may not exactly honor these values and instead use a value that is
the nearest valid value it can handle. Use the attributes described below to
be sure the scope does what you want.

If you provide values that the scope is unable to honor (eg. too many
samples or unsupported resolution), an
{exc}`~secbench.api.exceptions.InvalidHorizontalSetupError` will be raised.
```

+++

You can retrieve the scope horizontal parameters:

```{code-cell} ipython3
print("horizontal_samples:", scope.horizontal_samples())
print("horizontal_duration:", scope.horizontal_duration(), "seconds")
print("horizontal_interval:", scope.horizontal_interval(), "seconds")
```

```{warning}
For some scope devices, it is important to respect the setup order described
in this section, that is:

1. first, setup all channels
2. then, setup horizontal parameters (timebase).

This is because the horizontal resolution may depend on the number of
active channels.
```

+++

(sec:scope-trigger)=

### Trigger setup

Once the channels and horizontal parameters are setup, it is necessary to
configure the scope trigger condition:

```{code-cell} ipython3
# trigger on channel 1, rising slope above 1.5 V
scope.set_trigger("1", slope=Slope.rising, level=1.5)

# trigger on channel 2, falling slope below -100 mV
scope.set_trigger("2", slope=Slope.falling, level=-100e-3)
```

You can use either the channel name or a channel reference for the first parameter. The two methods below are equivalent:

```{code-cell} ipython3
scope.set_trigger("1", Slope.rising, 1.5)

scope["1"].set_trigger(Slope.rising, 1.5)
```

#### Trigger out feature

On supported hardware, it is possible to enable a *trigger out* signal, that is
a pulse of chosen width and delay after a trigger occurs:

```{code-cell} ipython3
# 1 ns pulse with a 1 µs delay
scope.enable_trigger_out(Slope.rising, length=1e-9, delay=1e-6)
```

### Channel arithmetic

On hardware that supports it, it is possible to apply an arithmetic function on
a channel that will be computed directly by the scope. The performances are
usually better than computing these on the computer.

For example, computing an average waveform for channel `1` on 40 triggers can
be accomplished using:

```{code-cell} ipython3
scope["1"].set_arithmetic(Arithmetic.average, reset=40)
```

This method is usually coupled with an acquisition count equal to the reset
count, as explained in the next section.

+++

## Segmented Acquisition Flow

Acquisition campaigns often consist in gathering several hundreds of thousands of traces.
To speed-up the trace gathering process, it is possible to acquire batches of traces.
It is particularly useful when using an aggregation function such as an average.
This approached is usually called "segmented acquisitions" or "batch acquisitions".

The flow will look like this:

```{eval-rst}
.. graphviz::

   digraph G {
      rankdir = TB;
      segmented -> arm -> reset -> wait -> acquire;
      reset -> reset [label="N iterations"];
      arm [label="Arm the scope"];
      segmented [label="Enable segmented acquisition (count=N)"]
      reset [label="Reset/send to DUT", style=filled, color=grey];
      wait [label="Wait for N triggers"];
      acquire [label="Recover N traces"];
   }
```

+++

Here is an example of how to acquire a batch with segmented acquisition:

```{code-cell} ipython3
# Setup a batch of 1000 traces
scope.set_horizontal(samples=100, interval=1e-9)
scope.segmented_acquisition(20)

scope.arm()
for i in range(20):
    # NOTE: this method is specific to SimulatedScope, just for demo purposes.
    # In practice, you should make your device under test trigger. Something like:
    # dut.do_some_crypto_op()
    scope.force_trigger()
scope.wait()
traces, = scope.get_data('1')
```

The `traces` array has shape:

```{code-cell} ipython3
print(traces.shape)
```

The different functions used in this code snippet are explained hereafter.

+++

### Arming and waiting for trigger

Once the scope is completely setup (channels, horizontal parameters and trigger
condition), it is possible to arm the acquisition. When the
{meth}`~secbench.api.instrument.Scope.arm` method returns, it means the scope is ready
to get triggered:

```{code-cell} ipython3
scope.disable_segmented_acquisition()
scope.arm()
# scope is now ready to trigger
```

Once arming is done, one has to wait for an actual trigger to happen. This is
accomplished using the {meth}`~secbench.api.instrument.Scope.wait` method. It will block
the program execution until the scope has been triggered:

```{code-cell} ipython3
# For the demo, we force a trigger on the scope.
scope.force_trigger()

scope.wait()
# scope has been triggered
```

In your side-channel acquisition, you have the ability to do any interaction with the
{term}`DUT` between these two calls. At the very least, the {term}`DUT` should
make the scope trigger on its configured trigger channel so that
{meth}`~secbench.api.instrument.Scope.wait` can return. A typical scenario will look
like this:

```{code-cell} ipython3
scope.arm()

# the line below should make the DUT send a trig signal
# my_dut.do_something('foobar')
scope.force_trigger()

scope.wait()
```

Do not forget to call {meth}`~secbench.api.instrument.Scope.arm` before triggering the
scope, because you will miss triggers without it.

Do not use hard-coded {func}`~time.sleep` calls, always use
{meth}`~secbench.api.instrument.Scope.wait` before acquiring scope data.

### Retrieving waveforms from the scope

Once the scope has triggered, the traces (waveforms) can be retrieved from the
scope for further processing or {ref}`storage <module-storage>`. In this example
the waveforms for channels 1 and 4 are retrieved:

```{code-cell} ipython3
traces = scope.get_data("1", "3")
# traces[0] is channel 1, traces[1] is channel 3
```

```{code-cell} ipython3
print(traces[0].shape, traces[1].shape)
```

Or use Python's unpacking syntax:

```{code-cell} ipython3
c1_data, c4_data = scope.get_data("1", "3")
```

```{note}
If you need the waveform of a single channel, don't forget to add a
**trailing comma**: `trace, = scope.get_data('1')`
```

The returned traces are flat NumPy arrays which size (number of points) is
equal to {meth}`~secbench.api.instrument.Scope.horizontal_samples`:

```{code-cell} ipython3
print("horizontal_samples:", scope.horizontal_samples())
print("c1_data.size", c1_data.size)
```

The values returned by {meth}`~secbench.api.instrument.Scope.get_data` are, by
default, raw samples in the device internal format, typically 8 or 16 bit
integers:

```{code-cell} ipython3
trace, = scope.get_data('1')
print(trace.dtype)
```

If you need volt readings, use `volts=True`:

```python
trace_in_volts, = scope.get_data('1', volts=True)
print(trace_in_volts.dtype)
```

+++

```{warning}
Based on our experience, it is not a good practice to query data in volts. The conversion in volts forces a conversion of the dataset in float, which will increase your storage size by a factor 4 in the worst case.

A better approach is to:
- Save the raw ADC samples in a dataset, which is minimal in space usage.
- Save the channel configuration in the dataset.
- When reloading the dataset if you truely need volts, do the conversion in memory.
```

```{code-cell} ipython3

```
