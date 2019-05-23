# nws_radar

A python library to get radar images from NWS.

Currently, only short range images are supported.

## Example

```python
import nws_radar
radar = nws_radar.Nws_Radar('VWX', 'NCR')
radar.update()
radar.image('radar.gif')
```

![radar](images/radar.gif?raw=true "radar")
