"""Asynchronous Python client for TRMNL."""

from collections.abc import AsyncGenerator, Generator

import aiohttp
from aioresponses import aioresponses
import pytest

from syrupy import SnapshotAssertion
from trmnl import TRMNLClient

from .syrupy import TRMNLSnapshotExtension


@pytest.fixture(name="snapshot")
def snapshot_assertion(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture with the TRMNL extension."""
    return snapshot.use_extension(TRMNLSnapshotExtension)


@pytest.fixture
async def client() -> AsyncGenerator[TRMNLClient, None]:
    """Return a TRMNL client."""
    async with (
        aiohttp.ClientSession() as session,
        TRMNLClient("token", session=session) as trmnl_client,
    ):
        yield trmnl_client


@pytest.fixture(name="responses")
def aioresponses_fixture() -> Generator[aioresponses, None, None]:
    """Return aioresponses fixture."""
    with aioresponses() as mocked_responses:
        yield mocked_responses
