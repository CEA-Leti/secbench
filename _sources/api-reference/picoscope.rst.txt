.. py:module:: secbench.picoscope

.. _module-picoscope:

Module: ``secbench.picoscope``
==============================

The :py:mod:`secbench.picoscope` module contains drivers for `Picoscope oscilloscopes <https://www.picotech.com/products/oscilloscope>`__.

This module requires Picoscope libraries to be installed. 
You can install the `PicoSDK <https://www.picotech.com/downloads>`__ or simply

The package requires to have in your library path:

- For :py:class:`~PicoPS6000Scope`:

    - ``libps6000.so`` on Unix systems
    - ``ps6000.dll`` on Window

- For :py:class:`~PicoPS2000AScope`:

    - ``libps2000a.so`` on Unix systems
    - ``ps2000a.dll`` on Window

.. note::

    On Linux, we recommend to set the correct permissions on the USB ports to avoid running scripts as root.
    You can add the following line in ``/lib/udev/rules.d/99-secbench.rules``:

    .. code-block:: text

        SUBSYSTEMS=="usb", ATTRS{idVendor}=="0ce9", MODE="0660", GROUP="plugdev"

    Make sure you are in the ``plugdev`` group.

Usage
-----

Once everything is installed and a scope is connected to your computer, you
should be able to load a device with:

.. code-block:: python

    from secbench.api import get_bench

    bench = get_bench()
    scope = bench.get_scope()
    print(scope)

The :py:mod:`secbench.api` automatically tries to import :py:mod:`secbench.picoscope` so that the devices are discoverable.

Supported models
----------------

.. autoclass:: secbench.picoscope.PicoPS2000AScope

.. autoclass:: secbench.picoscope.PicoPS6000Scope
