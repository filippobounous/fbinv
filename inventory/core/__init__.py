"""Inventory core module and submodules."""

from .mapping import BaseMappingEntity
from .item import Item
from .house import House
from .room import Room

__all__ = ["BaseMappingEntity", "Item", "House", "Room"]
