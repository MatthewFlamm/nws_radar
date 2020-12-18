# nws_radar

> :warning: This library is broken due to changes in NWS radar servers.

A python library to get radar images from NWS.

![PyPI - Downloads](https://img.shields.io/pypi/dm/nws-radar?style=flat-square)

## Example

```python
import nws_radar
radar = nws_radar.Nws_Radar('VWX', 'NCR')
radar.update()
radar.image('radar.gif')
```

![radar](images/radar.gif?raw=true "radar")
