"""Handles Clients in the Coinbase Exchange Library.

.. module:: client
   :synopsis: Client Handling

.. moduleauthor:: Alexander Simeonov <agsimeon@buffalo.edu>

"""
from builtins import map
from datetime import datetime

from requests.compat import urljoin, quote

from cbexchange.error import get_api_error


class APIClient(object):
  """Base class of all client in the Coinbase Exchange Library."""
  def _to_float(self, message, key):
    """Converts a value in the message to float.

    :param dict message: the input message
    :param str key: associated value will be converted to float

    """
    message[key] = float(message[key])

  def _to_datetime(self, message, key):
    """Converts a value in the message to datetime.datetime.

    :param dict message: the input message
    :param str key: associated value will be converted to datetime.datetime

    """
    message[key] = datetime.strptime(message[key], '%Y-%m-%dT%H:%M:%S.%fZ')

class RESTClient(APIClient):
  """Base class of all clients using the REST API.

  :param str api_uri: Coinbase Exchange REST API URI.

  """
  API_URI = 'https://api.exchange.coinbase.com'

  def __init__(self, api_uri=None):
    self.API_URI = api_uri or self.API_URI

  def _create_api_uri(self, *parts):
    """Creates fully qualified endpoint URIs.

    :param parts: the string parts that form the request URI

    """
    return urljoin(self.API_URI, '/'.join(map(quote, parts)))

  def _handle_response(self, response):
    """Returns requested data or raises an APIError for non-2xx responses.

    :param requests.Response response: HTTP response
    :returns: requested data
    :raises APIError: for non-2xx responses

    """
    if not str(response.status_code).startswith('2'):
      raise get_api_error(response)
    return response.json()

  def _get(self, *args, **kwargs):
    """Performs HTTP GET requests.

    :param args: arguments
    :param kwargs: argument keywords
    :returns: requested data
    :raises APIError: for non-2xx responses

    """
    return self._request('get', *args, **kwargs)
