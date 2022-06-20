from __future__ import annotations

import json
import logging
import requests

from datetime import datetime

from .const import (
    POLLEN_IDS,
    REGION_IDS,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)

POLLEN_URL = "https://www.astma-allergi.dk/umbraco/Api/PollenApi/GetPollenFeed"


class Pollen_DK:
    def __init__(self, regionIDs, pollenIDs):
        self._regionIDs = regionIDs
        self._regions = {}
        self._pollenIDs = pollenIDs
        self._session = requests.Session()

    def update(self):
        r = self._session.get(POLLEN_URL)
        if r.status_code == 200:
            r_json = json.loads(r.json())
            for regionID in r_json.keys():
                if int(regionID) in self._regionIDs:
                    self._regions[regionID] = PollenRegion(
                        int(regionID), self._pollenIDs, r_json[regionID]
                    )

    def getRegions(self):
        return self._regions.values()


class PollenRegion:
    def __init__(self, regionID, pollenIDs, rawData):
        self._ID = regionID
        self._pollenIDs = pollenIDs
        self._name = list(REGION_IDS.keys())[list(REGION_IDS.values()).index(regionID)]
        self._date = rawData["date"]
        self._pollenTypes = {}

        for pollenID, pollenData in rawData["data"].items():
            if int(pollenID) in self._pollenIDs:
                self._pollenTypes[pollenID] = PollenType(
                    int(pollenID), pollenData, self._date
                )

    def getID(self):
        return self._ID

    def getName(self):
        return self._name

    def getDate(self):
        return self._date

    def getPollenTypes(self):
        return self._pollenTypes.values()


class PollenType:
    def __init__(self, pollenID, rawData, date):
        self._ID = pollenID
        self._name = list(POLLEN_IDS.keys())[
            list(POLLEN_IDS.values()).index(pollenID)
        ].title()
        self._date = date
        self._inSeason = rawData["inSeason"]
        self._level = rawData["level"]
        self._predictions = []

        for date, dateKey in rawData["predictions"].items():
            level = dateKey["prediction"]
            if level:
                self._predictions.append(PollenPrediction(date, int(level)))

    def getID(self):
        return self._ID

    def getName(self):
        return self._name

    def getDate(self):
        return self._date

    def getInSeason(self):
        return self._inSeason

    def getLevel(self):
        return self._level

    def getPredictions(self):
        return self._predictions


class PollenPrediction:
    def __init__(self, date, level):
        self._date = date
        self._level = level

    def getDate(self):
        return self._date

    def getLevel(self):
        return self._level


# pollen = Pollen_DK()
# pollen.update()
