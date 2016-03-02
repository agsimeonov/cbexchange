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
  
  def _format_iso_time(self, time):
    """Makes sure we have proper ISO 8601 time.

    :param time: either already ISO 8601 a string or datetime.datetime
    :returns: ISO 8601 time
    :rtype: str

    """
    if isinstance(time, str):
      return time
    elif isinstance(time, datetime):
      return time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    else:
      return None

  def _handle_response(self, response):
    """Returns the given response or raises an APIError for non-2xx responses.

    :param requests.Response response: HTTP response
    :returns: requested data
    :rtype: requests.Response
    :raises APIError: for non-2xx responses

    """
    if not str(response.status_code).startswith('2'):
      raise get_api_error(response)
    return response

  def _request(self, method, *relative_path_parts, **kwargs):
    """Abstract method - must be overriden."""
    raise NotImplementedError

  def _get(self, *args, **kwargs):
    """Performs HTTP GET requests.

    :param args: arguments
    :param kwargs: argument keywords
    :returns: requested data
    :raises APIError: for non-2xx responses

    """
    return self._request('get', *args, **kwargs)

  def _post(self, *args, **kwargs):
    """Performs HTTP POST requests.

    :param args: arguments
    :param kwargs: argument keywords
    :returns: requested data
    :raises APIError: for non-2xx responses

    """
    return self._request('post', *args, **kwargs)

  def _delete(self, *args, **kwargs):
    """Performs HTTP POST requests.

    :param args: arguments
    :param kwargs: argument keywords
    :returns: requested data
    :raises APIError: for non-2xx responses

    """
    return self._request('post', *args, **kwargs)

class PaginationClient(RESTClient):
  """Handles Pagination `<https://docs.exchange.coinbase.com/#pagination>`_

  This client is iterable in the given direction (before parameter).

  :param str api_uri: Coinbase Exchange REST API URI.
  :param bool before: if True goes to the page before (older) else after (newer)
  :param int limit: number of results per request. Maximum 100. (default 100)
  :param cursor: the cursor you want to start at (default latest)

  """
  def __init__(self, api_uri=None, before=True, limit=None, cursor=None):
    super(PaginationClient, self).__init__(api_uri)
    self.before = before
    self.limit = limit
    self.before_cursor = None
    self.after_cursor = None
    if cursor:
      self.is_initial = False
      if before:
        self.before_cursor = cursor
      else:
        self.after_cursor = cursor
    else:
      self.is_initial = True

  def __iter__(self):
    return self

  def __next__(self):
    """Iterator function for Python 3.

    :returns: the next message in the sequence
    :raises StopIteration: if there are no more messages

    """
    next = self.endpoint()
    if next is not None:
      return next
    raise StopIteration

  # Iterator function for Python 2.
  next = __next__

  def _get_params(self, **kwargs):
    params = kwargs.get('params', {})
    params['limit'] = self.limit
    if not self.is_initial:
      if self.before:
        params['before'] = self.before_cursor
      else:
        params['after'] = self.after_cursor
    return params

  def _check_next(self):
    """Checks if a next message is possible.

    :returns: True if a next message is possible, otherwise False
    :rtype: bool

    """
    if self.is_initial:
      return True
    if self.before:
      if self.before_cursor:
        return True
      else:
        return False
    else:
      if self.after_cursor:
        return True
      else:
        return False

  def is_before(self):
    """Returns True if the direction is set to before.

    :returns: True if the direction is set to before, otherwise False
    :rtype: bool

    """
    return self.before

  def is_after(self):
    """Returns True if the direction is set to after.

    :returns: True if the direction is set to after, otherwise False
    :rtype: bool

    """
    return not self.before

  def set_before(self):
    """Sets the direction to before."""
    self.before = True

  def set_after(self):
    """Sets the direction to after."""
    self.before = False

  def endpoint(self):
    """Abstract method - must be overriden. Performs the endpoint operation"""
    raise NotImplementedError

  def get_before_cursor(self):
    """Acquires the before cursor.

    :returns: the before cursor

    """
    return self.before_cursor

  def get_after_cursor(self):
    """Acquires the after cursor.

    :returns: the after cursor

    """
    return self.after_cursor
