"""
Helper module for handling URLs.

This module contains functions to open URLs in the default web browser.
"""

import webbrowser

def open_url(url):
    """
    Open a URL in the default web browser.
    
    Args:
        url: The URL to open
    """
    webbrowser.open(url)
