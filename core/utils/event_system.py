"""
Simple event system to allow communication between different parts of the application.
"""
import weakref
from functools import partial
import threading
from core.utils.logger import debug, error, exception

class EventSystem:
    """
    Singleton event system for managing application events using weak references.
    """
    _instance = None
    _lock = threading.RLock()
    
    @classmethod
    def _get_instance(cls):
        """Get or create the singleton instance with proper thread safety."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the event system."""
        self._subscribers = {}
        self._weak_refs = {}
    
    @classmethod
    def subscribe(cls, event_name, callback, weak=False):
        """
        Subscribe to an event.
        
        Args:
            event_name (str): Name of the event
            callback (callable): Function to call when the event is published
            weak (bool): If True, use a weak reference to prevent memory leaks
        """
        instance = cls._get_instance()
        
        with cls._lock:
            if event_name not in instance._subscribers:
                instance._subscribers[event_name] = []
                instance._weak_refs[event_name] = {}
            
            # Don't add duplicate callbacks
            if callback in instance._subscribers[event_name]:
                return
                
            if weak:
                # Create a weak reference callback proxy
                if hasattr(callback, '__self__') and callback.__self__ is not None:
                    # This is a method, create a weak reference to the instance
                    obj = callback.__self__
                    method_name = callback.__name__
                    
                    # Create weak ref that removes itself when object is garbage collected
                    def remove_dead_ref(ref, event=event_name, method=method_name):
                        with cls._lock:
                            if event in instance._weak_refs:
                                if method in instance._weak_refs[event]:
                                    instance._weak_refs[event].pop(method, None)
                                    
                    weak_ref = weakref.ref(obj, remove_dead_ref)
                    instance._weak_refs[event_name][method_name] = (weak_ref, method_name)
                    
                    # Create a proxy function that calls the method on the weak reference
                    def weak_method_proxy(*args, **kwargs):
                        ref = instance._weak_refs[event_name].get(method_name)
                        if ref:
                            obj_ref = ref[0]()
                            if obj_ref is not None:
                                method = getattr(obj_ref, method_name, None)
                                if method:
                                    return method(*args, **kwargs)
                        return None
                    
                    instance._subscribers[event_name].append(weak_method_proxy)
                else:
                    # For simple functions, just add them directly
                    instance._subscribers[event_name].append(callback)
            else:
                # Add the callback directly for strong references
                instance._subscribers[event_name].append(callback)
                
            # debug(f"Subscribed to event '{event_name}' with {'weak' if weak else 'strong'} reference")
    
    @classmethod
    def unsubscribe(cls, event_name, callback):
        """
        Unsubscribe from an event.
        
        Args:
            event_name (str): Name of the event
            callback (callable): Function to remove from subscribers
        """
        instance = cls._get_instance()
        
        with cls._lock:
            if event_name not in instance._subscribers:
                return
                
            # Check if this is a method
            if hasattr(callback, '__self__') and callback.__self__ is not None:
                method_name = callback.__name__
                
                # Remove from weak references
                if event_name in instance._weak_refs:
                    instance._weak_refs[event_name].pop(method_name, None)
                
                # Try to find and remove matching proxies
                to_remove = []
                for cb in instance._subscribers[event_name]:
                    # Not a reliable way to identify, but checking name is our best option
                    if hasattr(cb, '__name__') and cb.__name__ == method_name:
                        to_remove.append(cb)
                
                for cb in to_remove:
                    try:
                        instance._subscribers[event_name].remove(cb)
                    except ValueError:
                        pass
            else:
                # For regular functions, just remove them directly
                try:
                    instance._subscribers[event_name].remove(callback)
                except ValueError:
                    pass
    
    @classmethod
    def publish(cls, event_name, *args, **kwargs):
        """
        Publish an event.
        
        Args:
            event_name (str): Name of the event
            *args, **kwargs: Arguments to pass to the subscribers
        """
        instance = cls._get_instance()
        callbacks = []
        
        # Get a copy of subscribers to avoid modification during iteration
        with cls._lock:
            if event_name in instance._subscribers:
                callbacks = instance._subscribers[event_name].copy()
        
        # Call each subscriber
        for callback in callbacks:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                exception(e, f"Error in event handler for '{event_name}'")
    
    @classmethod
    def clear_all(cls):
        """Clear all event subscriptions."""
        instance = cls._get_instance()
        
        with cls._lock:
            instance._subscribers.clear()
            instance._weak_refs.clear()
            debug("Cleared all event subscriptions")
