(sec:custom_instrument)=

# Creating Drivers for Instruments

In this tutorial, we describe how to integrate your own instruments (scopes, pulsers, AFGs, 3-axis tables) with {py:mod}`secbench.api`.
Here, we take the example of {py:class}`~secbench.api.instrument.Scope` implementation, but the approach would be the same with other type of instruments.

## Step 1: Implement an Abstract Instrument

If your instrument is based on command (SCPI or similar), we highly recommend
that you inherit {py:class}`~secbench.api.instrument.InstrumentMixin` class and implement
its functions. This mixin exposes the functions of the communication backend to
the current hardware, such as {py:meth}`~secbench.api.instrument.InstrumentMixin.query`, {py:meth}`~secbench.api.instrument.InstrumentMixin.write`.

Then, you must implement the abstract methods of the {py:class}`~secbench.api.instrument.Scope` class.
Here how the implementation could look like:

```python
from secbench.api import InstrumentMixin, Backend, UserConfig, Discoverable
from secbench.api.instrument import Scope

class MySuperInstrument(InstrumentMixin, Scope):

    # ===
    # InstrumentMixin
    # ===
    @property
    def backend(self):
        return None

    @classmethod
    def from_backend(cls, backend: Backend, cfg: UserConfig):
        ...

    def has_error(self) -> bool:
        ...

    def pop_next_error(self) -> str | None:
        ...

    # ===
    # Scope Interface
    # ===

    @property
    def description(self) -> str:
        return "my super instrument"

    def horizontal(self, *, interval: float | None = None, duration: float | None = None,
                       samples: int = None) -> None:
        self.write(f"HORIZONTAL:INTERVAL {interval:E}")
        self.write(f"HORIZONTAL:SAMPLES {samples}")

    def horizontal_duration(self) -> float:
        return float(self.query("HORIZONTAL:DURATION?"))

    def _wait(self, iterations: int, poll_interval: float) -> float:
        t = time.perf_counter()
        for _ in range(iterations):
            busy = int(self.query("BUSY?"))
            if busy == 0:
                return time.perf_counter() - t
            time.sleep(poll_interval)
        raise InstrumentError("Reached timeout")

    def _wait_auto(self) -> float:
        # Number of seconds to wait
        ttw = 3
        return self._wait(1000 * ttw, 1e-3)

    # ... Other methods ...
```

Secbench also defines different mixin classes that can be implemented by your instrument, depending on its specific features such as:

- {py:class}`~secbench.api.WriteManyMixin`: interesting to implement if your instrument supports the reception of multiple SCPI commands at the same time.
- {py:class}`~secbench.api.HasSetupStorage`: defines methods that can load/store the instrument setup.
- {py:class}`~secbench.api.HasWaveformStorage`: some scopes can store locally waveforms, implement this class if you want to retrieve them.

## Step 2: Make your Instrument Discoverable

The secbench framework already proposes different backends to work with
instruments.  The idea is to subclass the "backend-agnostic" instrument
`MySuperInstrument` and inherit some mixin what will make it discoverable with
specific communication backends.  The following code shows how to make your
device discoverable over serial communication, or VISA backend (e.g. GPIB,
RS232, USB, Ethernet).

:::{note}
It is also possible to manually implement the {py:class}`~secbench.api.Discoverable`
interface. This would require slightly more code.
:::


```python
from secbench.api.backend import SerialDiscoverableMixin, PyVisaDiscoverableMixin


class MySuperInstrumentOverSerial(SerialDiscoverableMixin, Discoverable, MySuperInstrument):
    def _match_serial(cls, idn: str) -> bool:
        return idn == "XXAABB"


class MySuperInstrumentOverPyVisa(PyVisaDiscoverableMixin, Discoverable, MySuperInstrument):
    def _pyvisa_match_id(cls, rm, path: str) -> bool:
        return path == "INSTR:FOO"
```

Your scope is now discoverable. You should be able to obtain your instrument
with the following code:

```python
from secbench.api import get_bench

bench = get_bench()

my_scope = bench.get_scope()

# More specific requests:
my_scope = bench.get(MySuperInstrument)
my_scope = bench.get(MySuperInstrumentOverSerial)
```

## Adding a new Communication Backend

If your communication backend is not supported, you can implement your own by inheriting from {py:class}`secbench.api.Backend`.
Currently supported backends for instruments are implemented by the following classes:

- {py:class}`~secbench.api.backend.USBTMCBackend`
- {py:class}`~secbench.api.backend.PyVisaBackend`
- {py:class}`~secbench.api.backend.VXIBackend`
- {py:class}`~secbench.api.backend.SerialBackend`

```python
from secbench.api import Backend

class MyAwesomeBackend(Backend):

    # ===
    # Backend interface
    # ===

    def set_timeout(self, secs: float):
        """
        Set timeout for blocking operations. (optional)
        """
        ...

    # ... Other methods ...


class MyAwesomeBackendDiscoverableMixin(abc.ABC):
    @classmethod
    def discover(cls, hw_info: HardwareInfo):
        # Implementation of discover for this class.
        ...

    @classmethod
    def build(cls, hardware_info: HardwareInfo, args)
        backend = MyAwesomeBackend(args)
        return cls.from_backend(backend)


class MySuperInstrumentOverMyAwesomeBackend(MyAwesomeBackendDiscoverableMixin, Discoverable, MySuperInstrument):
    pass
```

```python
# You can load your scope with this
backend = MyAwesomeBackend("FOO")
scope = MySuperInstrument(backend)

# Or discover it from the bench
bench = get_bench()
scope = bench.get(Scope)
```
