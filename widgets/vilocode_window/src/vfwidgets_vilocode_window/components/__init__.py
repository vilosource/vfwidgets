"""UI components for ViloCodeWindow.

This module contains all visual components like ActivityBar, SideBar,
MainPane, AuxiliaryBar, TitleBar, and WindowControls.
"""

from .activity_bar import ActivityBar, ActivityBarItem
from .auxiliary_bar import AuxiliaryBar, AuxiliaryBarResizeHandle
from .sidebar import ResizeHandle, SideBar, SideBarHeader
from .title_bar import DraggableMenuBar, TitleBar
from .window_controls import WindowControls

__all__ = [
    "ActivityBar",
    "ActivityBarItem",
    "AuxiliaryBar",
    "AuxiliaryBarResizeHandle",
    "DraggableMenuBar",
    "ResizeHandle",
    "SideBar",
    "SideBarHeader",
    "TitleBar",
    "WindowControls",
]
