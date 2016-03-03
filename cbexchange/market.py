"""The Market Data API is an unauthenticated set of endpoints for retrieving
market data. These endpoints provide snapshots of market data. 

Find more here: `<https://docs.exchange.coinbase.com/#market-data>`_

.. module:: market
   :synopsis: Market Data API

.. moduleauthor:: Alexander Simeonov <agsimeon@buffalo.edu>

"""
from requests import get

from cbexchange.client import RESTClient, PaginationClient

# Levels for Get Product Order Book
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
    response = get(uri, params=kwargs.get('params', None))
    return self._handle_response(response).json()

  def get_products(self):
    """`<https://docs.exchange.coinbase.com/#get-products>`_"""
    return self._get('products')

  def get_product_order_book(self, level=None, product_id='BTC-USD'):
    """`<https://docs.exchange.coinbase.com/#get-product-order-book>`_"""
    return self._get('products', product_id, 'book', params={'level':level})

  def get_product_ticker(self, product_id='BTC-USD'):
    """`<https://docs.exchange.coinbase.com/#get-product-ticker>`_"""
    return self._get('products', product_id, 'ticker')

  def get_trades(self, product_id='BTC-USD'):
    """`<https://docs.exchange.coinbase.com/#get-trades>`_"""
    return self._get('products', product_id, 'trades')

  def get_historic_trades(self, start, end, granularity, product_id='BTC-USD'):
    """`<https://docs.exchange.coinbase.com/#get-historic-rates>`_

    :param start: either datetime.datetime or str in ISO 8601
    :param end: either datetime.datetime or str in ISO 8601
    :pram int granularity: desired timeslice in seconds
    :returns: desired data

    """
    params = {
      'start':self._format_iso_time(start),
      'end':self._format_iso_time(end),
      'granularity':granularity
    }
    return self._get('products', product_id, 'candles', params=params)

  def get_stats(self, product_id='BTC-USD'):
    """`<https://docs.exchange.coinbase.com/#get-24hr-stats>`_"""
    return self._get('products', product_id, 'stats')

  def get_currencies(self):
    """`<https://docs.exchange.coinbase.com/#get-currencies>`_"""
    return self._get('currencies')

  def get_time(self):
    """`<https://docs.exchange.coinbase.com/#time>`_"""
    return self._get('time')

class MarketPaginationClient(PaginationClient):
  def _request(self, method, *relative_path_parts, **kwargs):
    """Sends an HTTP request to the REST API and receives the requested data.
    Additionally sets up pagination cursors.

    :param str method: HTTP method name
    :param relative_path_parts: the relative paths for the request URI
    :param kwargs: argument keywords
    :returns: requested data
    :raises APIError: for non-2xx responses

    """
    uri = self._create_api_uri(*relative_path_parts)
    response = get(uri, params=self._get_params(**kwargs))
    self.is_initial = False
    self.before_cursor = response.headers.get('cb-before', None)
    self.after_cursor = response.headers.get('cb-after', None)
    return self._handle_response(response).json()

class GetTradesPagination(MarketPaginationClient):
  """`<https://docs.exchange.coinbase.com/#get-trades>`_"""
  def __init__(self,
               product_id='BTC-USD',
               api_uri=None,
               before=True,
               limit=None,
               cursor=None):
    super(GetTradesPagination, self).__init__(api_uri, before, limit, cursor)
    self.product_id = product_id

  def endpoint(self):
    if self._check_next():
      return self._get('products', self.product_id, 'trades')
    else:
      return None
