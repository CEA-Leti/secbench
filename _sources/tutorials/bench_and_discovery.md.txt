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

(sec:secbench-essential-concepts)=
# Bench and Device Discovery

The goal of this guide is to provide a deep understanding of the concept and design patterns used in secbench.

To get the best from this tutorial, here are some recommendations:
- The tutorial is written so that each section can be read (or executed) linearly.
- We recommend you to not rush this notebook, take the necessary time to understand the concepts. It will save you lot of time.
- If possible, run this tutorial in a notebook and try to play with the examples, modify them and see how they behave.

+++

## Logging Setup

In the secbench framework, many things are logged through the `logging` module. By default those message would not be visible in an application, since logging is not configured. Enabling logging is a good way to inspect what is going on. For most application, we recommend using `logging.INFO` or `logging.WARNING`. The `logging.DEBUG` mode is very verbose and can be helpful when things do not work.

The following will initialize logging with `logging.INFO` level.

```{code-cell} ipython3
import logging

logging.basicConfig(level=logging.INFO)
```

Note that we can also enable logging for specific part of the framework. For example to turn debug messages only in the `secbench.api.backend` function, we can use:

```python
logging.getLogger("secbench.api.backend").setLevel(logging.DEBUG)
```

There are many other possiblities with logging, please refer to the  [logging module](https://docs.python.org/3/library/logging.html) documentation for more information.

+++

(sec:understanting-the-bench)=

## Creating a Bench

The {py:class}`~secbench.api.Bench` is defined in {py:mod}`secbench.api` module. It is a central concept in *Secbench*. Put shortly, a {py:class}`~secbench.api.Bench` is an helper to discover and instanciate lab hardware such as scopes, XYZ-Tables.

```{code-cell} ipython3
from secbench.api import get_bench, Discoverable, Bench, HardwareInfo

import numpy as np
```

A bench can be created as follows:

```{code-cell} ipython3
local_bench = Bench()
local_bench
```

Alternatively, you can also call {py:func}`secbench.api.get_bench`, which implements a singleton pattern. It returns a reference to a internal bench.

```{code-cell} ipython3
bench = get_bench()
```

Futher calls to `get_bench` will always return the same bench object:

```{code-cell} ipython3
print(bench)
print(get_bench())
```

Unless you have specific needs (e.g., you must have two different benches in your process), we recommend you to use the {py:func}`secbench.api.get_bench` method.

+++

## Hardware Discovery

+++

A bench allows discovery of any hardware **in the current scope** that implements the {py:class}`secbench.api.Discoverable` interface.

Let define a trivial {py:class}`~secbench.api.Discoverable` class for a fake instrument.

```{code-cell} ipython3
class StrangeHardware:
    pass
```

```{code-cell} ipython3
class MyDummyInstrument(Discoverable, StrangeHardware):
    def __init__(self, usb_port: str):
        self.usb_port = usb_port
        
    def arm(self):
        pass
    
    def wait(self):
        pass
    
    def get_data(self):
        return np.random.random(size=(10, 100))
    
    # Discoverable interface
    
    @classmethod
    def discover(cls, hardware_info: HardwareInfo):
        # Since the dummy hardware is always 
        # available, we always return it.
        yield "/dev/fooUSB0"
        
    @classmethod
    def build(cls, hardware_info: HardwareInfo, dev_path: str):
        return cls(dev_path)
```

Now, this `MyDummyInstrument` should be available for discovery.

An instrument can be discovered by calling {py:meth}`secbench.api.Bench.get` with the expected hardware type.

```{code-cell} ipython3
obj = bench.get(MyDummyInstrument)
```

```{code-cell} ipython3
print(obj, obj.usb_port)
```

Note that if you call again `bench.get` for the same type of hardware, the function will give you the same Python object.

```{code-cell} ipython3
print(bench.get(MyDummyInstrument))
```

If you don't want this behavior and force the instanciation of a new object, you can add `cache=False` to the `Bench.get`.

```{code-cell} ipython3
print(bench.get(MyDummyInstrument, cache=False))
```

```{code-cell} ipython3
print(bench.get(MyDummyInstrument))
```

You can also look for all subclasses. This is useful if you want to get any hardware that implement an interface, such as {py:class}`secbench.api.Instrument.Scope`.

```{code-cell} ipython3
print(bench.get(StrangeHardware))
```

If needed you can clear all cached hardware:

```{code-cell} ipython3
bench.clear_cache()
```

## Common Hardware Abstractions

+++

In the {py:mod}`secbench.api` package, we define abstract interfaces for typical hardware. For example:

- {py:class}`~secbench.api.instrument.Scope` for oscilloscopes
- {py:class}`~secbench.api.instrument.Pulser` for fault injection benches
- {py:class}`~secbench.api.instrument.Afg` for arbitrary function generators

The actual drivers (e.g., Picoscope, NewAE, Tektronix, R&S, ...) are implemented in their own packages (e.g., {py:mod}`secbench.picoscope`).

To see what an instrument driver looks like, you can take a look at the code:

Lets say you want to load a scope, here is how you would do. For this example, we will add the argument `required=False` so that this notebook can still execute without any scope connected.

```{code-cell} ipython3
from secbench.api.instrument import Scope, Afg, Pulser
```

```{code-cell} ipython3
scope = bench.get(Scope, required=False)
afg = bench.get(Afg, required=False)
pulser = bench.get(Pulser, required=False)
print("scope:", scope)
print("afg:", afg)
print("pulser", pulser)
```

For common instrument type, the {py:class}`~secbench.api.Bench` has methods for loading them without needing an additional import.

```{code-cell} ipython3
scope = bench.get(Scope, required=False)
# Is the same as:
scope = bench.get_scope(required=False)
```

### Registering Custom Hardware (Bypassing Discovery)

There are two common situations where you want to bypass discovery:

- When you want to make accessible hardware that cannot implement the `Discoverable` interface. 
- When multiple instances of the same hardware (e.g., 2 thermal sensors) are available and you want to use a specific one.

In both cases, you want the {py:meth}`secbench.api.Bench.get` method to return a specific hardware.

To achieve that, all you need to do is register your hardware in the bench as follows.

```{code-cell} ipython3
obj = MyDummyInstrument("A-CUSTOM-TTY")
obj
```

If we call `get`, a different new MyDummyInstrument instance will be created.

```{code-cell} ipython3
obj_2 = bench.get(MyDummyInstrument)
print("Same objects?", obj_2 == obj)
```

Which is not what we want. To avoid that, lets register `obj` manually.

```{code-cell} ipython3
# Clear the cache (otherwise, we would get obj_2)
bench.clear_cache()

bench.register(obj)
```

Now the `get` method behaves as expected:

```{code-cell} ipython3
obj_2 = bench.get(MyDummyInstrument)
print("Same objects?", obj_2 == obj)
```

```{code-cell} ipython3

```
