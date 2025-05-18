"""
Simple event system to allow communication between different parts of the application.
"""
from core.utils.logger import debug

class EventSystem:
    """
    A simple event system that allows components to subscribe to and publish events.
    """
    _subscribers = {}

    @classmethod
    def subscribe(cls, event_name, callback):
        """
        Subscribe a callback function to an event.
        
        Args:
            event_name (str): The name of the event to subscribe to
            callback (callable): The function to call when the event is published
        """
        if event_name not in cls._subscribers:
            cls._subscribers[event_name] = []
        
        cls._subscribers[event_name].append(callback)
        debug(f"Subscribed to event: {event_name}")
        
    @classmethod
    def unsubscribe(cls, event_name, callback):
        """
        Unsubscribe a callback from an event.
        
        Args:
            event_name (str): The name of the event
            callback (callable): The function to unsubscribe
        """
        if event_name in cls._subscribers and callback in cls._subscribers[event_name]:
            cls._subscribers[event_name].remove(callback)
            debug(f"Unsubscribed from event: {event_name}")
    
    @classmethod
    def publish(cls, event_name, *args, **kwargs):
        """
        Publish an event, calling all subscribers.
        
        Args:
            event_name (str): The name of the event to publish
            *args, **kwargs: Arguments to pass to the subscribers
        """
        if event_name in cls._subscribers:
            for callback in cls._subscribers[event_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    from core.utils.logger import exception
                    exception(e, f"Error in event subscriber for {event_name}")
            debug(f"Published event: {event_name}")
