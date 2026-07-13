from abc import ABC, abstractmethod


class BaseObserver(ABC):
    @abstractmethod
    def update(self, sender=None, instance=None, created=None, **kwargs):
        """
            Update method that is sent when the signal is called.
            sender: The model that sent the
            kwargs: Additional data_base_farm like instance, created, etc.
        """
        pass


class BaseObserverNotification(ABC):
    @abstractmethod
    def update(self, user=None, title=None, message=None, **kwargs):
        """

        """
        pass
