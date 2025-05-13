.. _module-processing:

.. py:module:: secbench.processing

Module: ``secbench.processing``
===============================

The :py:mod:`secbench.processing` module contains Secbench's processing tools
to support side-channel analysis. It is divided into several "thematic"
submodules (``secbench.processing.SUBMODULE``):

- :ref:`helpers <sec_processing_helpers>`: contains general purposes helpers and low-level functions useful for side-channel analysis.
- :ref:`metrics <sec_processing_models>`: contains functions to implement different leakage models.
- :ref:`metrics <sec_processing_metrics>`: contains side-channel
  leakage metrics. These metrics are fully compatible with the ``sklearn`` 
  API (they can be used as score functions).
- :ref:`profiled <sec_processing_profiled>`: contains tools for performing
  profiled (template attacks, neural networks).
- :ref:`signal <sec_processing_signal>`: contains many tools for filtering traces and synchronization.

- :ref:`crypto <sec_processing_crypto>`: simulation models for cryptographic primitives. The :ref:`AES model <sec_processing_aes>` is very useful.


.. _sec_processing_helpers:

Helpers
-------

The submodule :py:mod:`secbench.processing.helpers` contains general purposes
helpers useful for side-channel analysis.

.. autofunction:: secbench.processing.helpers.qplot

.. autofunction:: secbench.processing.helpers.rank_of

.. autofunction:: secbench.processing.helpers.key_scores

.. autofunction:: secbench.processing.helpers.encode_labels

.. autofunction:: secbench.processing.helpers.chunks

.. autofunction:: secbench.processing.helpers.add_remove

.. _sec_processing_models:

Leakage models
--------------

We provide numpy-optimized versions of the Hamming weight and Hamming distance
functions.

.. autofunction:: secbench.processing.models.hamming_weight

.. autofunction:: secbench.processing.models.hamming_distance

The following functions allow to perform various bit decompositions:

.. autofunction:: secbench.processing.models.unpackbits

.. autofunction:: secbench.processing.models.lra_unpackbits

.. autofunction:: secbench.processing.models.lra_unpackbits_2nd_order

.. autofunction:: secbench.processing.models.lra_unpackbits_shd

.. _sec_processing_metrics:

Leakage Metrics
---------------

The namespace :py:mod:`secbench.processing.metrics` contains common leakage
metrics used in side-channel analysis.

All those metrics are compliant with ``sklearn`` scoring API.
This allows you to do things like:

.. code-block:: python

    from sklearn.feature_selection import SelectKBest
    import secbench.processing.metrics as metrics

    # Keep 20 highest SNR points
    selector = SelectKBest(metrics.snr_accumulator, k=20)
    selector.fit(data, ciphertexts)
    print(selector.get_support())
    print(selector.scores_)

Furthermore, you can also use these metrics as part of a ``sklearn`` pipeline.
Here is a 4-line "template attack" pipeline (parameters may be tuned).

.. code-block:: python

    from sklearn.pipeline import make_pipeline
    from sklearn.feature_selection import SelectKBest
    from sklearn.decomposion import PCA

    pipeline = make_pipeline(
        SelectKBest(metrics.nicv, k=100),
        PCA(n_components=5),
        QuadraticDiscriminantAnalysis())
    pipeline.fit(X_train, y_train)
    print(pipeline.score(X_valid, y_valid))

Currently, the following metrics are supported. All of them are univariate:

- :py:func:`metrics.snr`
- :py:func:`metrics.welch_t_test`
- :py:func:`metrics.nicv`
- :py:func:`metrics.sost`
- :py:func:`metrics.pearson`
- :py:class:`metrics.LRA`

.. autofunction:: secbench.processing.metrics.snr

.. autofunction:: secbench.processing.metrics.welch_t_test

.. autofunction:: secbench.processing.metrics.nicv

.. autofunction:: secbench.processing.metrics.sost

.. autofunction:: secbench.processing.metrics.pearson

The LRA class allows various kind of linear regression analysis.

.. autoclass:: secbench.processing.metrics.LRA
    :members:
    :undoc-members:

Under the hoods, most univariate metrics seen before are computed using a so-called "conditional mean and variance".
The latter is just the mean and variance of traces grouped per label value.

For leakage assessment, we highly recommend to:

- compute a condition mean and variance **once**
- (if your dataset is huge) then save the result somewhere for latter re-use
- finally, *freeze* the metrics you actually need.

The easiest way to compute conditional mean and variance is through the :py:func:`~secbench.processing.metrics.cond_mean_var` function.
This function returns a :py:class:`~secbench.processing.metrics.CondMeanVar`.

.. autofunction:: secbench.processing.metrics.cond_mean_var

.. note::

    The conditional mean and variance is implemented as an accumulator. It means you
    can feed new data in an existing instance.


From a :py:class:`~secbench.processing.metrics.CondMeanVar` instance, you can do many operations on it.
The implementation is done in Rust, is heavily optimized and multi-threaded.

.. autoclass:: secbench.processing.metrics.CondMeanVar
    :members:
    :inherited-members:

Perceived Information
~~~~~~~~~~~~~~~~~~~~~

The perceived information is a tool to evaluate the quality of a model. It should converge towards the
mutual information, but is guaranteed to be lower (assuming the model is not overfitting).

.. autofunction:: secbench.processing.metrics.perceived_information

.. _sec_processing_profiled:

Profiled Attacks
----------------

The attack variants implemented in :py:mod:`secbench.processing.profiled` subclass the :py:class:`~profiled.ProfiledAttack` interface.
You will typically implement the following workflow:

1. Create a :py:class:`~profiled.ProfiledAttack` instance (depending on the model you want).
#. Train it using :py:meth:`~profiled.ProfiledAttack.fit`,
#. Run it on attack data, using either :py:meth:`~profiled.ProfiledAttack.key_scores` (blackbox attack)
   or :py:meth:`~profiled.ProfiledAttack.guessing_entropy` (for evaluation).

We currently provide two main models:

1. :py:class:`~profiled.SklearnModel`, which can wrap any ``Estimator`` from Sklearn.
#. :py:class:`~profiled.ScaNetwork`, which is designed to wrap a Tensorflow network. You can pass an
    arbitrary tensorflow network. For simple cases, we provide a easy interface to create a network: :py:class:`~profiled.GenericNetworkBuilder`.

Abstract interface
~~~~~~~~~~~~~~~~~~

.. autoclass:: secbench.processing.profiled.ProfiledAttack
    :members:
    :undoc-members:

Sklearn wrapper
~~~~~~~~~~~~~~~

.. autoclass:: secbench.processing.profiled.SklearnModel
    :members:
    :undoc-members:


Tensorflow neural network wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: secbench.processing.profiled.ScaNetwork
    :members:
    :undoc-members:

.. autoclass:: secbench.processing.profiled.GenericNetworkBuilder
    :members:
    :undoc-members:

Other tools
~~~~~~~~~~~

.. autoclass:: secbench.processing.profiled.ClassPCA
    :members:
    :undoc-members:


.. _sec_processing_crypto:

Cryptographic Models
--------------------

The :py:mod:`secbench.processing.crypto` provides simulation models for
cryptographic algorithm. Those models can be used to compute intermediate
variables for side-channel analysis.

PCG32 Random Generator Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: secbench.processing.crypto.Pcg32
    :members:
    :undoc-members:

.. _sec_processing_aes:

AES
~~~

AES is the most frequently targeted algorithm for side-channel analysis.

AES Common Constants
````````````````````

.. autofunction:: secbench.processing.crypto.aes.aes_nist_key

.. autofunction:: secbench.processing.crypto.aes.aes_sbox

.. autofunction:: secbench.processing.crypto.aes.aes_sbox_leakage

.. autofunction:: secbench.processing.crypto.aes.aes_inv_sbox

Models of T-Tables (e.g., used by OpenSSL implementations):

.. autofunction:: secbench.processing.crypto.aes.aes_t_table

.. autofunction:: secbench.processing.crypto.aes.aes_t_indices

Key Expansion
`````````````

- Forward: :py:func:`aes.aes_expand_key` (all rounds), :py:func:`aes.aes_expand_key_step` (single step)
- Inverse: :py:func:`aes.aes_inv_expand_key` (all rounds), :py:func:`aes.aes_inv_expand_key_step` (single step)

.. autofunction:: secbench.processing.crypto.aes.aes_expand_key

.. autofunction:: secbench.processing.crypto.aes.aes_expand_key_step

.. autofunction:: secbench.processing.crypto.aes.aes_inv_expand_key

.. autofunction:: secbench.processing.crypto.aes.aes_inv_expand_key_step

Functional Model
````````````````

Functional model of the core AES operations are available in the namespace :py:class:`aes.AesOps` class.

For side-channel and the computation of intermediate values, we provide a flexible implementation of the AES.
The class :py:class:`aes.AES` allows to stop execution at any round.
Execution can also be resumed from any round.
Here is an example usage:

.. code-block:: python

    from secbench.processing.crypto.aes import AesOps, AES

    key = np.array(
        [0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c],
        dtype=np.uint8)
    pts = np.random.randint(0, 256, size=(10, 16), dtype=np.uint8)

    cipher = AES(key)

    # Normal Encryption
    ciphertexts = cipher.encrypt(pts)

    # Stop after the sub_bytes of 3rd round
    intermediates = cipher.encrypt(pts, stop_round=3, stop_after=AesOps.sub_bytes)
    # Finish encryption
    finished = cipher.encrypt(intermediates, start_round=3, start_after=AesOps.sub_bytes)
    # Encrypt until the round 5
    intermediates = cipher.encrypt(pts, stop_round=5)
    # Finish encryption
    cipher.encrypt(intermediates, start_round=6)

The same thing can be done with the AES decryption (``decrypt`` method).

.. autoclass:: secbench.processing.crypto.aes.AesOps
    :members:
    :undoc-members:

.. autoclass:: secbench.processing.crypto.aes.AES
    :members:
    :member-order: bysource

Input Generators
````````````````

We implement several helpers to generate inputs for side-channel leakage assessments.

.. autofunction:: secbench.processing.crypto.aes.generate_plaintexts

.. autofunction:: secbench.processing.crypto.aes.biased_state_plaintexts

.. autofunction:: secbench.processing.crypto.aes.generate_round_states

.. autofunction:: secbench.processing.crypto.aes.biased_hd_plaintexts

CRC8
~~~~

.. autofunction:: secbench.processing.crypto.crc8.crc8

.. _sec_processing_signal:

Signal Processing
-----------------

Fourier Transforms and Filtering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: secbench.processing.signal.rfft_mag

.. autofunction:: secbench.processing.signal.fft_filter

.. autofunction:: secbench.processing.signal.generate_lp_firls

.. autofunction:: secbench.processing.signal.plot_filter_response

.. autofunction:: secbench.processing.signal.plot_fft

.. autofunction:: secbench.processing.signal.spectrogram

Synchronization
~~~~~~~~~~~~~~~

We recommend that you take a look at the notebook tutorial
(:ref:`sec-pattern_matching_tutorial`) that shows how to use those functions.

.. autofunction:: secbench.processing.signal.match_correlation

.. autofunction:: secbench.processing.signal.match_euclidean

.. autofunction:: secbench.processing.signal.phase_correlation

Misc
~~~~

.. autofunction:: secbench.processing.signal.downsample

.. autofunction:: secbench.processing.signal.sliding_mean

.. autofunction:: secbench.processing.signal.sliding_var

.. autofunction:: secbench.processing.signal.sliding_std

.. autofunction:: secbench.processing.signal.sliding_skew

.. autofunction:: secbench.processing.signal.sliding_kurt