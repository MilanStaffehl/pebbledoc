Process a matrix using iterative refinement.

This function applies **iterative refinement** to a matrix using the
algorithm described in :meth:`_refine_step`, with *emphasis* on numerical
stability. It is a companion to :class:`MatrixProcessor` and relies on
:attr:`MatrixProcessor.default_tolerance` for its stopping condition.

The refinement minimizes the residual

.. math::

    \| A x - b \|_2^2 + \lambda \| x \|_2^2

where :math:`\lambda` is the regularization ``threshold`` parameter. For a
single element, the update rule is :math:`x_{i+1} = x_i - \alpha \nabla f(x_i)`.

Typical usage:

.. code-block:: python

    matrix = load_matrix("data.csv")
    result = process_matrix(matrix, threshold=0.1)
    print(result.shape)

A quick interactive check:

>>> process_matrix([[1, 0], [0, 1]], threshold=0.0)
array([[1., 0.],
       [0., 1.]])

Supported normalization strategies:

1. Row-wise normalization (default)

   1. Normalization to max
   2. Normalization to unity

2. Column-wise normalization

   1. Normalization to max
   2. Normalization to unity

3. No normalization (``normalize=False``)

Related considerations:

- Numerical stability improves with lower ``threshold`` values

  - The lowest threshold value of ``0.5`` should not be undercut.
  - Values below ``0.01`` typically lead to excessive runtimes for no benefit.

- Convergence is not guaranteed for singular matrices
- See also `related discussion <#notes>`_ below

.. note::

   This function mutates ``data`` in place when ``normalize=True``.
   Pass a copy if you need to preserve the original matrix.

.. danger::

   Do not use this function on matrices containing NaN values — the
   refinement loop will not terminate and may hang the process.

.. version-removed:: 2.1.0

        Support for tensors was moved to :mod:`tensors`.

:param data: A **required** list of ``float`` lists representing the
    input matrix. See :meth:`_validate_matrix` for shape constraints.
:param threshold: Convergence threshold as a ``float``. Lower values
    increase precision at the cost of more iterations:

    - ``0.5`` -- fast, low precision (default)
    - ``0.1`` -- balanced
    - ``0.01`` -- slow, high precision

:param normalize: Whether to normalize rows before refinement.
:raises ValueError: If ``data`` is empty or not rectangular.
:raises TypeError: If elements of ``data`` are not numeric.
:returns: The refined matrix as a nested ``list``, with the same shape
    as the input. See :attr:`MatrixProcessor.output_format` for
    alternate return types.
