import numpy


class LimitConfig(object):
    """ Class to handle configuration parameters for each spectrum.

    In limit setting we want to be able to add multiple backgrounds and
    a signal spectrum. Each background will have a different range of
    counts to use in floating it and some will be constrained by a
    penalty term. This class keeps track of all this information.

    Attributes:
      _prior_counts (float): prior/expected counts
      _counts (list): list of count rates (*float*) to use for scaling
      _sigma (float): prior constraint on counts
      _chi_squareds (:class:`numpy.array`): Array col-0:
        :obj:`chi_squared`, col-1: :obj:`get_counts`, col-2:
        :meth:`spectra.sum()`.

    Args:
      prior_counts (float): prior/expected counts
      counts (list): list of count (*float*) to use for scaling
      sigma (float, optional): prior constraint on counts
    """
    def __init__(self, prior_count, counts, sigma=None):
        self._prior_count = prior_count
        self._counts = counts
        self._sigma = sigma
        self._chi_squareds = numpy.zeros(shape=(3, 0), dtype=float)

    def get_count(self):
        """
        Yields:
          float: next count in array

        Examples:
          When dealing with multiple backgrounds, just select the
          corresponding config for each background (e.g. ``bkg_config``)
          then you can correctly loop over the background scalings

          >>> for count in bkg_config.get_count():
          ...     spectrum.scale(count)
          ...     # spectrum scaled to each value of count

        Attributes:
          _current_count (float): current count (scaling). The value
            most recently returned by :meth:`get_count()`
        """
        for count in self._counts:
            self._current_count = count
            yield count

    def add_chi_squared(self, chi_squared, scaling, events):
        """ Add chi squared to config chi squared array.

        Args:
          chi_squared (float): chi squared value to add
        """
        entry_to_append = numpy.zeros((3, 1))
        entry_to_append[0][0] = chi_squared
        entry_to_append[1][0] = scaling
        entry_to_append[2][0] = events
        # Append new entry, axis is 1 as we are appending an entry not a column
        self._chi_squareds = numpy.append(self._chi_squareds,
                                          entry_to_append, axis=1)

    def get_minimum(self):
        """ Get minimum value from chi_squared array.

        Returns:
          float: Minimum of :attr:`_chi_squareds`
        """
        return numpy.min(self._chi_squareds[0])

    def get_first_bin_above(self, limit):
        """ For signal, determine the count corresponding to limit.

        The limit count is the first count value that takes the chi
        squared over the threshold set by the desired confidence limit.

        Args:
          limit (float): chi squared value corresponding to desired
            confidence limit

        Returns:
          float: number of events (result of
            :meth:`echidna.core.spectra.Spectra.sum()`) at limit
        """
        return self._chi_squareds[2, numpy.where(self._chi_squareds[0] > limit)[0][0]]

    def reset_chi_squareds(self):
        """ Resets :attr:`_chi_squareds` to an empty
          :class:`numpy.ndarray`
        """
        self._chi_squareds = numpy.zeros(shape=(3, 0), dtype=float)
