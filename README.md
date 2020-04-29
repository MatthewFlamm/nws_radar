# nws_radar

A python library to get radar images from NWS.

## Example

```python
import nws_radar
radar = nws_radar.Nws_Radar('VWX', 'NCR')
radar.update()
radar.image('radar.gif')
```

![radar](images/radar.gif?raw=true "radar")
