"""The Market Data API is an unauthenticated set of endpoints for retrieving 
   market data. These endpoints provide snapshots of market data. 
   Find more here: https://docs.exchange.coinbase.com/#market-data

.. module:: market
   :synopsis: Market Data API

.. moduleauthor:: Alexander Simeonov <agsimeon@buffalo.edu>

"""
from requests import get

from cbexchange.client import RESTClient


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
    return self._handle_response(get(uri))
