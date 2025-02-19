.. py:module:: secbench.storage

.. _module-storage:

Module: ``secbench.storage``
============================

This is the API documentation for the :py:mod:`secbench.storage` module. An :ref:`interactive user-guide <sec:secbench-storage-walkthrough>` is also available.

You will use mainly two classes from this module:

- :py:class:`~Store`, the storage abstraction layer. A :py:class:`~Store` contains zero or more :py:class:`~Datasets`.
- :py:class:`~Dataset`, which allow to access and modify datasets.

Shared datasets
---------------

Over the years, we accumulated several datasets from real targets. To list the datasets available use:

.. code-block:: console

    $ secbench-db list -l

From Python, you can use :py:func:`secbench.storage.load_shared_dataset`. If you need to list datasets, use :py:func:`secbench.storage.shared_datasets`.

.. autofunction:: secbench.storage.load_shared_dataset

.. autofunction:: secbench.storage.shared_datasets

Storage types
-------------

The :py:class:`Store` class is the top-level accessor for dataset.

.. autoclass:: secbench.storage.Store
    :members:
    :inherited-members:
    :member-order: bysource

Then, the :py:class:`Dataset` class is used to manage individual datasets.

.. autoclass:: secbench.storage.Dataset
    :members:
    :member-order: bysource

.. autoclass:: secbench.storage.DatasetRef
    :members:
    :member-order: bysource

Helpers
-------

.. autofunction:: secbench.storage.version
