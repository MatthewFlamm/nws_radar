"""NWS radar image"""
from io import BytesIO
import re

from bs4 import BeautifulSoup
from PIL import Image
import requests

from .const import (
    url_base, url_layer, url_radar, url_legend, url_warning)

BASE_LAYER = 'Topo'
OVER_LAYERS = ['County', 'Highways', 'Cities', 'RangeRings']
DISTS = ['Short'] # Long not yet supported


class Nws_Radar:
    """
    NWS radar images.  Get images and assemble into looping GIF.
    """

    def __init__(self, station, product, dist='Short', nframes=5):
        """Initialize."""
        self.station = station
        self.product = product
        if dist not in DISTS:
            raise ValueError
        self.dist = dist
        if nframes < 0:
            raise ValueError
        self.nframes = nframes

        self.url_radar = url_radar(self.product, self.station)
        self.url_legend = url_legend(self.product, self.station)
        self.url_warning = url_warning(self.station, self.dist)
        self._image_base = None
        self._image_overlays = None
        self._images_radar = None
        self._images_legend = None
        self._images_warning = None

        self._legend_files = None
        self._radar_files = None
        self._warning_files = None

    def update(self):
        """
        Get new images if available.

        For static images, only get once.
        For changing images, first get list of files, then match files,
        then get all images.
        """
        if self._image_overlays is None:
            self._image_overlays = self._get_image_overlays()
        if self._image_base is None:
            self._image_base = self._get_base_image()

        self._radar_files = self._get_mult_files(self.url_radar)
        self._legend_files = self._get_mult_files(self.url_legend)
        self._warning_files = self._get_mult_files(self.url_warning)

        self._validate_file_list()
        self._images_radar = self._update_mult_images(self.url_radar,
                                                      self._radar_files)
        self._images_legend = self._update_mult_images(self.url_legend,
                                                       self._legend_files)
        self._images_warning = self._update_mult_images(self.url_warning,
                                                        self._warning_files)

    @staticmethod
    def retrieve_image(url):
        """Get image from url."""
        res = requests.get(url, stream=True)
        res.raw.decode_content = True
        return Image.open(res.raw)

    def _get_image_overlays(self):
        """Get static overlays."""
        image_overlays = []
        for overlay in OVER_LAYERS:
            url = url_layer(overlay, self.station, self.dist)
            imag = self.retrieve_image(url)
            image_overlays.append(imag.convert('RGBA'))
        return image_overlays

    @staticmethod
    def _get_mult_files(url):
        """Get list of GIFS at url."""
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        links = soup.findAll(href=re.compile(r"\.gif$"))
        files = [link.get('href') for link in links]
        return files

    def _update_mult_images(self, url, files):
        """Get list of images. """
        file_urls = [url + f for f in files]
        nframes = self.nframes
        if nframes > len(self._radar_files):
            nframes = len(self._radar_files)

        images = []
        for f in file_urls[-nframes:]:
            imag = self.retrieve_image(f)
            images.append(imag.convert('RGBA'))
        return images

    def _get_base_image(self):
        """Get base image."""
        url = url_base(BASE_LAYER, self.station, self.dist)
        imag = self.retrieve_image(url)
        return imag.convert('RGBA')

    @staticmethod
    def _time_extract(files):
        """Return tuple of time for matching files."""
        return [tuple(f.split('_')[1:3]) for f in files]

    def _validate_file_list(self):
        """Only keep matching files."""
        self._warning_files = [f for f in self._warning_files
                               if self.dist not in f]

        radar_ts = self._time_extract(self._radar_files)
        legend_ts = self._time_extract(self._legend_files)
        warning_ts = self._time_extract(self._warning_files)
        self._radar_files = [
            f for k, f in zip(radar_ts, self._radar_files)
            if k in legend_ts and k in warning_ts]
        self._legend_files = [
            f for k, f in zip(legend_ts, self._legend_files)
            if k in radar_ts and k in warning_ts]
        self._warning_files = [
            f for k, f in zip(warning_ts, self._warning_files)
            if k in legend_ts and k in radar_ts]

    def image(self, outfile=None):
        """
        Generate looping image.

        If outfile, save to outfile.
        Else, return BytesIO object.
        """
        b = BytesIO()
        frames = [self._gen_frame(radar, legend, warning)
                  for radar, legend, warning in
                  zip(self._images_radar, self._images_legend, self._images_warning)]
        if frames:
            frames.extend([frames[-1]] * 2)
            frames[0].save(b, format='gif', save_all=True,
                           append_images=frames[1:], loop=0, duration=500)
        else:
            Image.new('RGB', (600, 550)).save(b, format='gif')
        if outfile is not None:
            with open(outfile, 'wb') as fi:
                fi.write(b.getvalue())
        return b.getvalue()


    def _gen_frame(self, image_radar, image_legend, image_warning):
        """Make a single frame."""
        image_comb = Image.alpha_composite(self._image_base, image_radar)
        for overlay in self._image_overlays:
            image_comb.alpha_composite(overlay)
        image_comb.alpha_composite(image_legend)
        image_comb.alpha_composite(image_warning)
        return image_comb
