"""Handles Errors in the Coinbase Exchange Library.

.. module:: error
  :synopsis: Error Handling

.. moduleauthor:: Alexander Simeonov <agsimeon@buffalo.edu>

"""


class CBExchangeError(Exception):
  """All Coinbase Exchange Library related errors extend this class."""

class APIError(CBExchangeError):
  """Unless otherwise stated, errors to bad requests will respond with HTTP 4xx 
  or status codes. The body will also contain a message parameter indicating the
  cause. Your language's http library should be configured to provide message
  bodies for non-2xx requests so that you can read the message field from the
  body. Find more here: `<https://docs.exchange.coinbase.com/#errors>`_

  :param requests.Response response: HTTP error response

  """

  def __init__(self, response):
    self.status_code = response.status_code
    self.message = response.json().get('message')

  def __str__(self):
    error_string = '%s(%i)' % (self.__class__.__name__, self.status_code)
    if self.message:
      error_string += ': %s' % self.message
    return error_string

class BadRequestError(APIError): pass      # 400
class UnauthorizedError(APIError): pass    # 401
class ForbiddenError(APIError): pass       # 403
class NotFoundError(APIError): pass        # 404
class TooManyRequestsError(APIError): pass # 429
class InternalServerError(APIError): pass  # 500

def get_api_error(response):
  """Acquires the correct error for a given response.

  :param requests.Response response: HTTP error response
  :returns: the appropriate error for a given response
  :rtype: APIError

  """
  error_class = _status_code_to_class.get(response.status_code, APIError)
  return error_class(response)

_status_code_to_class = {
  400: BadRequestError,
  401: UnauthorizedError,
  403: ForbiddenError,
  404: NotFoundError,
  429: TooManyRequestsError,
  500: InternalServerError
}
