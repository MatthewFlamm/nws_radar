import re
import shutil

from bs4 import BeautifulSoup
from PIL import Image
import requests

from nws_radar.const import (
    url_base, url_layer, url_radar, url_legend, url_warning)


BASE_LAYER = 'Topo'
OVER_LAYERS = ['County', 'Highways', 'Cities', 'RangeRings']


class Nws_Radar:
    """ """
    def __init__(self, station, product, dist, nframes=5):
        self.station = station
        self.product = product
        self.dist = dist
        self.nframes = nframes

        self._image_base = None
        self._image_overlays = None
        self._radar_files = None
        
    def update(self):
        """Get new images if available"""
        if self._image_overlays is None:
            self._image_overlays = self._get_image_overlays()
        if self._image_base is None:
            self._image_base = self._get_base_image()

        self._radar_files = self._get_radar_files()
        self._legend_files = self._get_legend_files()
        self._warning_files = self._get_warning_files()

        self._validate_file_list()
        self._update_radar_images()
        self._update_legend_images()
        self._update_warning_images()

    def _get_image_overlays(self):
        image_overlays = []
        for overlay in OVER_LAYERS:
            url = url_layer(overlay, self.station, self.dist)
            response_overlay = requests.get(url, stream=True)
            response_overlay.raw.decode_content = True
            image_overlays.append(Image.open(response_overlay.raw).convert('RGBA'))
        return image_overlays

    def _get_radar_files(self):
        url = url_radar(self.product, self.station)
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        radar_files = [link.get('href')
                       for link in soup.findAll(href=re.compile("\.gif$"))]
        return radar_files

    def _update_radar_images(self):
        radar_files = self._radar_files
        radars = [url_radar(self.product, self.station)
                  + rf for rf in radar_files]
        images_radar =[]
        for radar in radars[-self.nframes:]:
            response_radar = requests.get(radar, stream=True)
            response_radar.raw.decode_content = True
            images_radar.append(Image.open(response_radar.raw).convert('RGBA'))
        self._images_radar = images_radar

    def _get_legend_files(self):
        res = requests.get(url_legend(self.product, self.station))
        soup = BeautifulSoup(res.content, 'html.parser')
        legend_files = [link.get('href')  for link in soup.findAll(href=re.compile("\.gif$"))]
        return legend_files

    def _update_legend_images(self):
        legend_files = self._legend_files
        legends = [url_legend(self.product, self.station)
                   + leg for leg in legend_files]
        images_legend = []
        for legend in legends[-self.nframes:]:
            response_legend = requests.get(legend, stream=True)
            response_legend.raw.decode_content = True
            images_legend.append(Image.open(response_legend.raw).convert('RGBA'))
        self._images_legend = images_legend

    def _get_warning_files(self):
        url = url_warning(self.station, self.dist)
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        warning_files = [link.get('href') for link in soup.findAll(href=re.compile("\.gif$")) if self.dist in link.get('href')]
        return warning_files

    def _update_warning_images(self):
        warning_files = self._warning_files
        warnings = [url_warning(self.station, self.dist) + war for war in warning_files]
        images_warning = []
        for warning in warnings[-self.nframes:]:
            print(warning)
            response = requests.get(warning, stream=True)
            response.raw.decode_content = True
            images_warning.append(Image.open(response.raw).convert('RGBA'))
        self._images_warning = images_warning

        
    def _get_base_image(self):
        url = url_base(BASE_LAYER, self.station, self.dist)
        print(url)
        response_base = requests.get(url, stream=True)
        return Image.open(response_base.raw).convert('RGBA')

    @staticmethod
    def _time_extract(files):
        return [tuple(f.split('_')[1:3]) for f in files]
            
    def _validate_file_list(self):
        radar_ts = self._time_extract(self._radar_files)
        legend_ts = self._time_extract(self._legend_files)
        warning_ts = self._time_extract(self._warning_files)
        self._radar_files = [f for k, f in zip(radar_ts, self._radar_files) if k in legend_ts and k in warning_ts]
        self._legend_files = [f for k, f in zip(legend_ts, self._legend_files) if k in radar_ts and k in warning_ts]
        self._warning_files = [f for k, f in zip(warning_ts, self._warning_files) if k in legend_ts and k in radar_ts]
        

    def image(self, outfile=None):
        frames = [self._gen_frame(radar, legend, warning)
                  for radar, legend, warning in
                  zip(self._images_radar, self._images_legend, self._images_warning)]
        frames.extend([frames[-1]] * 2)
        if outfile is not None:
            frames[0].save(outfile, save_all=True, append_images=frames[1:], loop=0, duration=500)
        else:
            return frames

    def _gen_frame(self, image_radar, image_legend, image_warning):
        image_comb = Image.alpha_composite(self._image_base, image_radar)
        for overlay in self._image_overlays:
            image_comb.alpha_composite(overlay)
        image_comb.alpha_composite(image_legend)
        image_comb.alpha_composite(image_warning)
        return image_comb
