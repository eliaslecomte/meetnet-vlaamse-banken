"""Regression tests for setup failures and coordinator refreshes."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from homeassistant.config_entries import ConfigEntries, ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import frame
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.meetnet_vlaamse_banken import async_setup_entry
from custom_components.meetnet_vlaamse_banken.api import (
    AvailableData,
    Catalog,
    MeetnetApiClient,
    MeetnetAuthError,
    MeetnetConnectionError,
)
from custom_components.meetnet_vlaamse_banken.const import DOMAIN
from custom_components.meetnet_vlaamse_banken.coordinator import (
    MeetnetDataUpdateCoordinator,
)


@pytest_asyncio.fixture
async def setup_context(tmp_path, monkeypatch):
    """Use real HA coordinator behavior with only the API and platforms mocked."""
    hass = HomeAssistant(str(tmp_path))
    hass.config_entries = MagicMock(spec=ConfigEntries)
    monkeypatch.setattr(frame._hass, "hass", hass)
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "meetnet-test"
    entry.state = ConfigEntryState.SETUP_IN_PROGRESS
    entry.data = {
        "username": "test-user",
        "password": "test-password",
        "locations": ["NPT"],
    }
    api = MagicMock(spec=MeetnetApiClient)
    api.get_catalog = AsyncMock(return_value=Catalog({}, {}, []))
    api.get_current_data = AsyncMock(return_value={})
    api.get_available_data_for_locations.return_value = [
        AvailableData("NPTWVC", "NPT", "WVC")
    ]
    with (
        patch(
            "custom_components.meetnet_vlaamse_banken.async_get_clientsession"
        ),
        patch(
            "custom_components.meetnet_vlaamse_banken.MeetnetApiClient",
            return_value=api,
        ),
        patch.object(hass.config_entries, "async_forward_entry_setups", new=AsyncMock()),
    ):
        yield hass, entry, api
    await hass.async_stop(force=True)


@pytest.mark.asyncio
async def test_catalog_connection_failure_can_retry_and_recover(setup_context):
    """A transient catalog outage must escape setup as ConfigEntryNotReady."""
    hass, entry, api = setup_context
    outage = MeetnetConnectionError("API temporarily unavailable")
    api.get_catalog.side_effect = [outage, Catalog({}, {}, [])]

    with pytest.raises(ConfigEntryNotReady, match="Failed to fetch catalog") as exc:
        await async_setup_entry(hass, entry)
    assert exc.value.__cause__ is outage
    assert entry.entry_id not in hass.data[DOMAIN]
    api.get_current_data.assert_not_awaited()
    hass.config_entries.async_forward_entry_setups.assert_not_awaited()

    assert await async_setup_entry(hass, entry)
    api.get_current_data.assert_awaited_once_with(["NPTWVC"])
    assert entry.entry_id in hass.data[DOMAIN]
    hass.config_entries.async_forward_entry_setups.assert_awaited_once()


@pytest.mark.asyncio
async def test_catalog_auth_failure_still_requests_reauthentication(setup_context):
    """Invalid catalog credentials must not become a connection retry."""
    hass, entry, api = setup_context
    api.get_catalog.side_effect = MeetnetAuthError("Invalid credentials")

    with pytest.raises(ConfigEntryAuthFailed):
        await async_setup_entry(hass, entry)
    hass.config_entries.async_forward_entry_setups.assert_not_awaited()


@pytest.mark.asyncio
async def test_initial_data_connection_failure_can_retry(setup_context):
    """The first coordinator refresh must retain HA's setup retry behavior."""
    hass, entry, api = setup_context
    api.get_current_data.side_effect = MeetnetConnectionError("API unavailable")

    with pytest.raises(ConfigEntryNotReady):
        await async_setup_entry(hass, entry)
    assert entry.entry_id not in hass.data[DOMAIN]
    hass.config_entries.async_forward_entry_setups.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (MeetnetConnectionError("API unavailable"), UpdateFailed),
        (MeetnetAuthError("Invalid credentials"), ConfigEntryAuthFailed),
    ],
)
async def test_polling_preserves_failure_types(setup_context, error, expected):
    """Polling errors keep their distinct availability and auth semantics."""
    hass, entry, api = setup_context
    coordinator = MeetnetDataUpdateCoordinator(hass, api, entry)
    await coordinator.async_setup()
    api.get_current_data.side_effect = error

    with pytest.raises(expected):
        await coordinator._async_update_data()
