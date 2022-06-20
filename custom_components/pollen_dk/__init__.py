from __future__ import annotations

import logging

from .pollen_dk_api import Pollen_DK

from .const import (
    DOMAIN,
    CONF_CLIENT,
    CONF_PLATFORM,
    CONF_POLLEN_TYPES,
    CONF_REGIONS,
    POLLEN_IDS,
    REGION_IDS,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    # Get the configuration
    conf = config.get(DOMAIN)
    # If no config, abort
    if conf is None:
        return True

    regionIDs = []
    regions = config[DOMAIN].get(CONF_REGIONS, [])
    if regions:
        for regionKey in regions:
            for regionName, regionID in REGION_IDS.items():
                if regionKey in regionName.lower():
                    regionIDs.append(regionID)
    else:
        regionIDs = REGION_IDS.values()
    _LOGGER.debug(f"Region IDs loaded from config: { regionIDs }")

    pollenIDs = []
    pollens = config[DOMAIN].get(CONF_POLLEN_TYPES, [])
    if pollens:
        for pollenKey in pollens:
            for pollenName, pollenID in POLLEN_IDS.items():
                if pollenKey == pollenName.lower():
                    pollenIDs.append(pollenID)
    else:
        pollenIDs = POLLEN_IDS.values()
    _LOGGER.debug(f"Pollen IDs loaded from config: { pollenIDs }")

    hass.data[DOMAIN] = {CONF_CLIENT: Pollen_DK(regionIDs, pollenIDs)}

    # Add sensors
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform(CONF_PLATFORM, DOMAIN, conf, config)
    )

    # Initialization was successful.
    return True
