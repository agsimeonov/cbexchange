"""The Market Data API is an unauthenticated set of endpoints for retrieving 
   market data. These endpoints provide snapshots of market data. 
   
   Find more here: `<https://docs.exchange.coinbase.com/#market-data>`_

.. module:: market
   :synopsis: Market Data API

.. moduleauthor:: Alexander Simeonov <agsimeon@buffalo.edu>

"""
from requests import get

from cbexchange.client import RESTClient

LEVEL_BEST = 1
LEVEL_TOP  = 2
LEVEL_FULL = 3


class MarketClient(RESTClient):
  def _request(self, method, *relative_path_parts, **kwargs):
    """Sends an HTTP request to the REST API and receives the requested data.

    :param str method: HTTP method name
    :param relative_path_parts: the relative paths for the request URI
    :param kwargs: argument keywords
    :returns: requested data
    :raises APIError: for non-2xx responses

    """
    uri = self._create_api_uri(*relative_path_parts)
    return self._handle_response(get(uri, params=kwargs.get('params', None)))

  def get_products(self):
    """`<https://docs.exchange.coinbase.com/#get-products>`_"""
    return self._get('products')

  def get_product_order_book(self, product_id='BTC-USD', level=None):
    """`<https://docs.exchange.coinbase.com/#get-product-order-book>`_"""
    return self._get('products', product_id, 'book', params={'level':level})

  def get_product_ticker(self, product_id='BTC-USD'):
    """`<https://docs.exchange.coinbase.com/#get-product-ticker>`_"""
    return self._get('products', product_id, 'ticker')
