"""
TabAnimator component for smooth Chrome-style tab animations.

Provides 60 FPS animations for tab insertion, removal, hover effects, and reordering.
Uses Qt's property animation system for optimal performance.
"""

from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import (
    QEasingCurve,
    QObject,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QRect,
    Signal,
)
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget


class TabAnimator(QObject):
    """
    Handles all tab animations for smooth 60 FPS transitions.

    This class manages animations for:
    - Tab insertion (slide in from right)
    - Tab removal (collapse and slide left)
    - Hover effects (opacity fade)
    - Tab reordering (smooth position transitions)
    """

    animationFinished = Signal()
    insertionAnimationFinished = Signal(int)  # index
    removalAnimationFinished = Signal(int)  # index
    reorderAnimationFinished = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the tab animator."""
        super().__init__(parent)

        # Animation constants for Chrome-like feel
        self.INSERTION_DURATION = 200  # ms - smooth but not slow
        self.REMOVAL_DURATION = 150   # ms - snappier for removals
        self.HOVER_DURATION = 100     # ms - responsive hover
        self.REORDER_DURATION = 250   # ms - smooth reordering

        # Active animations tracking
        self.active_animations: List[QPropertyAnimation] = []
        self.animation_groups: List[QParallelAnimationGroup] = []

    def animate_tab_insertion(self, tab_bar, index: int) -> None:
        """
        Animate new tab sliding in from right.

        Implementation:
        1. Start tab at width=0
        2. Animate to full width over 200ms
        3. Use OutCubic easing for smooth deceleration

        Args:
            tab_bar: The ChromeTabBar widget
            index: Index where tab was inserted
        """
        if not hasattr(tab_bar, 'tabRect') or index >= tab_bar.count():
            return

        # Create animation for tab width expansion
        animation = QPropertyAnimation(tab_bar, b"geometry")
        animation.setDuration(self.INSERTION_DURATION)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Get target rect for the new tab
        target_rect = tab_bar.tabRect(index)

        # Start from zero width (simulate sliding in)
        start_rect = QRect(target_rect.left(), target_rect.top(), 0, target_rect.height())
        animation.setStartValue(start_rect)
        animation.setEndValue(target_rect)

        # Connect completion signal
        animation.finished.connect(lambda: self._on_insertion_finished(index))
        animation.finished.connect(lambda: self._cleanup_animation(animation))

        # Track and start animation
        self.active_animations.append(animation)
        animation.start()

        # Force tab bar to update during animation
        animation.valueChanged.connect(tab_bar.update)

    def animate_tab_removal(self, tab_bar, index: int) -> None:
        """
        Animate tab collapsing and others sliding left.

        Implementation:
        1. Animate removed tab width to 0
        2. Simultaneously slide other tabs left
        3. Duration: 150ms for snappy feel

        Args:
            tab_bar: The ChromeTabBar widget
            index: Index of tab being removed
        """
        if not hasattr(tab_bar, 'tabRect') or index >= tab_bar.count():
            return

        # Create parallel animation group for smooth combined effect
        group = QParallelAnimationGroup()

        # Animation for the tab being removed (collapse to width 0)
        removal_animation = QPropertyAnimation(tab_bar, b"geometry")
        removal_animation.setDuration(self.REMOVAL_DURATION)
        removal_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Get current rect and animate to zero width
        current_rect = tab_bar.tabRect(index)
        collapsed_rect = QRect(current_rect.left(), current_rect.top(), 0, current_rect.height())
        removal_animation.setStartValue(current_rect)
        removal_animation.setEndValue(collapsed_rect)

        group.addAnimation(removal_animation)

        # Animation for tabs sliding left (other tabs)
        for i in range(index + 1, tab_bar.count()):
            slide_animation = QPropertyAnimation(tab_bar, b"geometry")
            slide_animation.setDuration(self.REMOVAL_DURATION)
            slide_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

            tab_rect = tab_bar.tabRect(i)
            # Calculate new position (slide left by removed tab width)
            new_rect = QRect(
                tab_rect.left() - current_rect.width(),
                tab_rect.top(),
                tab_rect.width(),
                tab_rect.height()
            )
            slide_animation.setStartValue(tab_rect)
            slide_animation.setEndValue(new_rect)

            group.addAnimation(slide_animation)

        # Connect completion signals
        group.finished.connect(lambda: self._on_removal_finished(index))
        group.finished.connect(lambda: self._cleanup_animation_group(group))

        # Track and start animation group
        self.animation_groups.append(group)
        group.start()

        # Force tab bar to update during animation
        removal_animation.valueChanged.connect(tab_bar.update)

    def animate_hover(self, widget: QWidget, hover: bool) -> None:
        """
        Animate hover state with opacity fade.

        Implementation:
        1. Create QPropertyAnimation for opacity
        2. Fade in to 1.0 on hover, fade out to 0.9
        3. Duration: 100ms for responsive feel

        Args:
            widget: Widget to animate
            hover: True for hover in, False for hover out
        """
        if not widget:
            return

        # Get or create opacity effect
        opacity_effect = widget.graphicsEffect()
        if not isinstance(opacity_effect, QGraphicsOpacityEffect):
            opacity_effect = QGraphicsOpacityEffect()
            widget.setGraphicsEffect(opacity_effect)

        # Create opacity animation
        animation = QPropertyAnimation(opacity_effect, b"opacity")
        animation.setDuration(self.HOVER_DURATION)
        animation.setEasingCurve(QEasingCurve.Type.OutQuart)

        # Set start and end values
        current_opacity = opacity_effect.opacity()
        target_opacity = 1.0 if hover else 0.9

        animation.setStartValue(current_opacity)
        animation.setEndValue(target_opacity)

        # Connect completion signal
        animation.finished.connect(lambda: self._cleanup_animation(animation))

        # Track and start animation
        self.active_animations.append(animation)
        animation.start()

    def animate_tab_reorder(self, tab_bar, from_index: int, to_index: int) -> None:
        """
        Animate tab reordering with smooth position transitions.

        Args:
            tab_bar: The ChromeTabBar widget
            from_index: Original tab position
            to_index: Target tab position
        """
        if not hasattr(tab_bar, 'tabRect') or from_index == to_index:
            return

        # Create parallel animation group for all affected tabs
        group = QParallelAnimationGroup()

        # Determine which tabs need to move
        start_idx = min(from_index, to_index)
        end_idx = max(from_index, to_index)

        for i in range(start_idx, end_idx + 1):
            animation = QPropertyAnimation(tab_bar, b"geometry")
            animation.setDuration(self.REORDER_DURATION)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)

            current_rect = tab_bar.tabRect(i)

            # Calculate new position after reorder
            if i == from_index:
                # Main tab moving to new position
                target_rect = tab_bar.tabRect(to_index)
            elif from_index < to_index and start_idx <= i < from_index:
                # Tabs moving right
                target_rect = tab_bar.tabRect(i + 1)
            elif from_index > to_index and from_index < i <= end_idx:
                # Tabs moving left
                target_rect = tab_bar.tabRect(i - 1)
            else:
                continue  # No movement needed

            animation.setStartValue(current_rect)
            animation.setEndValue(target_rect)

            group.addAnimation(animation)

        # Connect completion signals
        group.finished.connect(lambda: self._on_reorder_finished())
        group.finished.connect(lambda: self._cleanup_animation_group(group))

        # Track and start animation group
        self.animation_groups.append(group)
        group.start()

        # Force tab bar to update during animation
        if group.animationCount() > 0:
            group.animationAt(0).valueChanged.connect(tab_bar.update)

    def stop_all_animations(self) -> None:
        """Stop all running animations immediately."""
        # Stop individual animations
        for animation in self.active_animations[:]:
            if animation.state() == QPropertyAnimation.State.Running:
                animation.stop()
            self._cleanup_animation(animation)

        # Stop animation groups
        for group in self.animation_groups[:]:
            if group.state() == QParallelAnimationGroup.State.Running:
                group.stop()
            self._cleanup_animation_group(group)

    def is_animating(self) -> bool:
        """Check if any animations are currently running."""
        return (
            any(anim.state() == QPropertyAnimation.State.Running for anim in self.active_animations) or
            any(group.state() == QParallelAnimationGroup.State.Running for group in self.animation_groups)
        )

    def _on_insertion_finished(self, index: int) -> None:
        """Handle insertion animation completion."""
        self.insertionAnimationFinished.emit(index)
        self.animationFinished.emit()

    def _on_removal_finished(self, index: int) -> None:
        """Handle removal animation completion."""
        self.removalAnimationFinished.emit(index)
        self.animationFinished.emit()

    def _on_reorder_finished(self) -> None:
        """Handle reorder animation completion."""
        self.reorderAnimationFinished.emit()
        self.animationFinished.emit()

    def _cleanup_animation(self, animation: QPropertyAnimation) -> None:
        """Clean up completed animation."""
        if animation in self.active_animations:
            self.active_animations.remove(animation)
        animation.deleteLater()

    def _cleanup_animation_group(self, group: QParallelAnimationGroup) -> None:
        """Clean up completed animation group."""
        if group in self.animation_groups:
            self.animation_groups.remove(group)
        group.deleteLater()
