"""NWS radar image"""
from io import BytesIO
import re

from bs4 import BeautifulSoup
from PIL import Image
import requests

from .const import url_lite


class Nws_Radar_Lite:
    """
    NWS radar images lite.  
    """

    def __init__(self, station, product, loop='True'):
        """Initialize."""
        self.station = station
        self.product = product
        self.loop = loop

        self.url_lite = url_lite(self.product, self.station, self.loop)
        self._image = None
        
    def update(self):
        """
        Get new images if available.
        """
        self._image = self.retrieve_image()
        
    def retrieve_image(self):
        """Get image from url."""
        res = requests.get(self.url_lite, stream=True)
        res.raw.decode_content = True
        return Image.open(res.raw)


    def image(self, outfile=None):
        """
        Generate looping image.

        If outfile, save to outfile.
        Else, return BytesIO object.
        """
        b = BytesIO()
        self._image.save(b, format='gif', save_all=True, loop=0)
        if outfile is not None:
            with open(outfile, 'wb') as fi:
                fi.write(b.getvalue())
        return b.getvalue()
