"""Constants and utility functions."""

FMT_BASE = 'http://radar.weather.gov/ridge/Overlays/{0}/{3}/{2}_{1}_{3}.jpg'
FMT_LAYER = 'http://radar.weather.gov/ridge/Overlays/{0}/{3}/{2}_{1}_{3}.gif'
FMT_RADAR = 'https://radar.weather.gov/ridge/RadarImg/{0}/{1}/'
FMT_LEGEND = 'http://radar.weather.gov/ridge/Legend/{0}/{1}/'
FMT_WARNING = 'http://radar.weather.gov/ridge/Warnings/{1}/{0}/'

DISTANCES = ['Short', 'Long']
OVERLAYS = {
    'Cities': 'City',
    'County': 'County',
    'Highways': 'Highways',
    'RangeRings': 'RangeRing',
}
BASES = ['Topo']


def validate_dis(dis):
    """Validate distance/range."""
    if dis not in DISTANCES:
        raise ValueError("{} not valid range".format(dis))


def validate_base(base):
    """Validate base type."""
    if base not in BASES:
        raise ValueError("{} not valid range".format(base))


def get_overlay(overlay):
    """Validate overlay and return second value."""
    if overlay not in OVERLAYS.keys():
        raise ValueError("{} not valid range".format(overlay))
    return OVERLAYS[overlay]


def url_base(base, stn, dis):
    """Return url base image."""
    validate_dis(dis)
    validate_base(base)
    return FMT_BASE.format(base, base, stn, dis)


def url_layer(layer, stn, dis):
    """Return url layer image."""
    validate_dis(dis)
    layer2 = get_overlay(layer)
    return FMT_LAYER.format(layer, layer2, stn, dis)


def url_radar(radar, stn):
    """Return url radar."""
    return FMT_RADAR.format(radar, stn)


def url_legend(radar, stn):
    """Return url legend."""
    return FMT_LEGEND.format(radar, stn)


def url_warning(radar, stn):
    """Return url warning."""
    return FMT_WARNING.format(radar, stn)
