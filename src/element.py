"""
Base class for accounting elements
"""

import abc


class Element(abc.ABC):
    """
    base class for accounting elements
    """

    @abc.abstractmethod
    def to_frame(self):
        """Output as a dataframe row"""
