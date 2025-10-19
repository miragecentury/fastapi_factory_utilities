"""Provides the abstract class for the Aiopika plugin."""

from abc import ABC
from typing import Self

from aio_pika.abc import AbstractChannel, AbstractRobustConnection

from .exceptions import AiopikaPluginBaseError, AiopikaPluginConnectionNotProvidedError


class AbstractAiopikaResource(ABC):
    """Abstract class for the Aiopika resource."""

    def __init__(self) -> None:
        """Initialize the Aiopika resource."""
        self._robust_connection: AbstractRobustConnection | None = None
        self._channel: AbstractChannel | None = None

    def set_robust_connection(self, robust_connection: AbstractRobustConnection) -> Self:
        """Set the robust connection."""
        self._robust_connection = robust_connection
        return self

    def set_channel(self, channel: AbstractChannel) -> Self:
        """Set the channel."""
        self._channel = channel
        return self

    async def _acquire_channel(self) -> AbstractChannel:
        """Acquire the channel."""
        if self._robust_connection is None:
            raise AiopikaPluginConnectionNotProvidedError(
                message="Robust connection not provided.",
            )
        if self._channel is None:
            try:
                self._channel = await self._robust_connection.channel()
            except Exception as exception:
                raise AiopikaPluginBaseError(
                    message="Failed to acquire the channel.",
                ) from exception
        return self._channel

    async def setup(self) -> Self:
        """Setup the Aiopika resource."""
        if self._channel is None:
            await self._acquire_channel()
        return self
