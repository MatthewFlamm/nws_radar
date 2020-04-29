"""NWS radar image"""
from io import BytesIO
import re

from bs4 import BeautifulSoup
from PIL import Image
import requests

from .const import URL_MOSAIC


REGIONS = [
    'NATAK',
    'NATPR',
    'NAT',
    'CENTGRTLAKES',
    'GREATLAKES',
    'HAWAII',
    'NORTHEAST',
    'NORTHROCKIES',
    'PACNORTHWEST',
    'PACSOUTHWEST',
    'SOUTHEAST',
    'SOUTHMISSVLY',
    'SOUTHPLAINS',
    'SOUTHROCKIES',
    'UPPERMISSVLY',
]


class Nws_Radar_Mosaic:
    """
    NWS radar mosaic images.  Get images and assemble into looping GIF.
    """

    def __init__(self, region, nframes=5):
        """Initialize."""
    
        if region.upper() not in REGIONS:
            raise ValueError(f"{region} not in supported values: {REGIONS}")
        self.region = region.upper()
        if nframes < 0:
            raise ValueError(f"nframes must be nonnegative, got {nframes}")
        self.nframes = nframes

        self._images = None

        self._files = None

    def update(self):
        """
        Get new images if available.

        For static images, only get once.
        For changing images, first get list of files, then match files,
        then get all images.
        """
        self._files = self._get_mult_files(URL_MOSAIC)

        self._validate_file_list()
        self._images = self._update_mult_images(URL_MOSAIC, self._files)

    @staticmethod
    def retrieve_image(url):
        """Get image from url."""
        res = requests.get(url, stream=True)
        res.raw.decode_content = True
        return Image.open(res.raw)

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
        if nframes > len(file_urls):
            nframes = len(file_urls)

        images = []
        for f in file_urls[-nframes:]:
            imag = self.retrieve_image(f)
            images.append(imag.convert('RGBA'))
        return images

    def _validate_file_list(self):
        """Only keep matching files."""
        self._files = [f for f in self._files
                       if len(f.split('_')) == 3]
        self._files = [f for f in self._files
                       if f.split('_')[0].upper() == self.region]

    def image(self, outfile=None):
        """
        Generate looping image.

        If outfile, save to outfile.
        Else, return BytesIO object.
        """
        b = BytesIO()
        if self._images:
            frames = self._images.copy()
            frames.extend([frames[-1]] * 2)
            frames[0].save(b, format='gif', save_all=True,
                           append_images=frames[1:], loop=0, duration=500)
        else:
            Image.new('RGB', (600, 550)).save(b, format='gif')
        if outfile is not None:
            with open(outfile, 'wb') as fi:
                fi.write(b.getvalue())
        return b.getvalue()
