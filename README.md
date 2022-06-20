# Pollen_DK

## Introduction
Scraping of pollen count in Denmark.

## Installation
### Custom integration in HACS
https://hacs.xyz/docs/faq/custom_repositories

## Configuration
In the default configuration it will track pollen in these regions of Denmark
- øst     # Øst for Stroebælt
- vest    # Vest for Stroebælt

Pollen type:
- Alternaria
- Birk
- Bynke
- Cladosporium
- El
- Elm
- Græs
- Hassel

## Configuration
### Minimal - track all pollentypes in all regions
```yaml
pollen_dk:
```
### Filtered - track only selected pollentypes in specific regions
```yaml
pollen_dk:
  # Optional values, if omitted all values will used
  regions:        # Possible values: øst, vest
    - vest
    - øst
  pollen_types:   # Possible values: alternaria, birk, bynke, cladosporium, el, elm, græs, hassel
    - græs
    - el
    - elm
```
