from __future__ import annotations

import logging

from homeassistant.const import ATTR_ATTRIBUTION
from .const import (
    CONF_CLIENT,
    CONF_PLATFORM,
    CREDITS,
    DOMAIN,
    NAME_PREFIX,
    UPDATE_INTERVAL,
)

from datetime import timedelta

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):

    # Define a update function
    async def async_update_data():
        # Retrieve the client stored in the hass data stack
        pollen_DK = hass.data[DOMAIN][CONF_CLIENT]
        # Call, and wait for it to finish, the function with the refresh procedure
        _LOGGER.debug("Updating pollen...")
        await hass.async_add_executor_job(pollen_DK.update)

    # Create a coordinator
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=CONF_PLATFORM,
        update_method=async_update_data,
        update_interval=timedelta(minutes=UPDATE_INTERVAL),
    )

    # Immediate refresh
    await coordinator.async_request_refresh()

    # Add the sensor to Home Assistant
    entities = []
    pollen_DK = hass.data[DOMAIN][CONF_CLIENT]
    regions = pollen_DK.getRegions()
    for region in regions:
        for pollen in region.getPollenTypes():
            entities.append(
                PollenSensor(hass, coordinator, region.getID(), pollen.getID(), len(regions))
            )
    async_add_entities(entities)


class PollenSensor(SensorEntity):
    def __init__(self, hass, coordinator, regionID, pollenID, regionsLen) -> None:
        self._hass = hass
        self._coordinator = coordinator
        self._regionID = regionID
        self._pollenID = pollenID
        self._regionsLen = regionsLen
        self._attr_state_class = SensorStateClass.MEASUREMENT

    def region(self):
        pollen_DK = self._hass.data[DOMAIN][CONF_CLIENT]
        return pollen_DK.getRegionByID(self._regionID)

    def pollen(self):
        return self.region().getPollenTypeByID(self._pollenID)


    @property
    def name(self):
        if self._regionsLen > 1:
            return f"{ NAME_PREFIX } {self.pollen().getName()} {self.region().getName().split()[0]}"
        else:
            return f"{ NAME_PREFIX } {self.pollen().getName()}"

    @property
    def icon(self):
        return "mdi:flower-pollen"

    @property
    def state(self):
        return self.pollen().getLevel()

    @property
    def unique_id(self):
        return f"33fecfc9590b4c098ab27d0f188b6d4e_{self.region().getID()}_{self.pollen().getID()}"

    @property
    def state_class(self) -> str:
        """Return the state class of the sensor."""
        return self._attr_state_class

    @property
    def extra_state_attributes(self):
        attr = {}

        attr["last_update"] = self.pollen().getDate()
        attr["in_season"] = self.pollen().getInSeason()
        attr["predictions"] = []
        for prediction in self.pollen().getPredictions():
            attr["predictions"].append(
                {"date": prediction.getDate(), "level": prediction.getLevel()}
            )
        attr[ATTR_ATTRIBUTION] = CREDITS

        return attr

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def available(self):
        """Return if entity is available."""
        return self._coordinator.last_update_success

    async def async_update(self):
        """Update the entity. Only used by the generic entity update service."""
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )
