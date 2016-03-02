"""Private endpoints are available for order management, and account management.
   Every private request must be signed using the described authentication 
   scheme.

   Find more here: `<https://docs.exchange.coinbase.com/#private>`_

.. module:: private
   :synopsis: Private API

.. moduleauthor:: Alexander Simeonov <agsimeon@buffalo.edu>

"""
from base64 import b64decode
from hashlib import sha256
from hmac import new
from time import time

from requests import get
from requests.auth import AuthBase

from cbexchange.client import RESTClient, PaginationClient


class CoinbaseExchangeAuth(AuthBase):
  """`<https://docs.exchange.coinbase.com/#authentication>`_

  :param str api_key: the API Key
  :param str secret_key: the base64-encoded signature
  :param str passphrase: the passphrase you specified when creating the API key

  """
  def __init__(self, api_key, secret_key, passphrase):
    self.api_key = api_key
    self.secret_key = secret_key
    self.passphrase = passphrase

  def __call__(self, request):
    timestamp = str(time())
    message = timestamp        + \
              request.method   + \
              request.path_url + \
              (request.body or '')
    hmac_key = b64decode(self.secret_key)
    signature = new(hmac_key, message, sha256)
    signature_b64 = signature.digest().encode('base64').rstrip('\n')

    request.headers.update({
      'CB-ACCESS-SIGN':signature_b64,
      'CB-ACCESS-TIMESTAMP':timestamp,
      'CB-ACCESS-KEY':self.api_key,
      'CB-ACCESS-PASSPHRASE':self.passphrase,
      'Content-Type':'application/json'
    })

    return request

class PrivateClient(RESTClient):
  """`<https://docs.exchange.coinbase.com/#authentication>`_

  :param CoinbaseExchangeAuth auth: authentication for the Private API
  :param str api_uri: Coinbase Exchange REST API URI

  """
  def __init__(self, auth, api_uri=None):
    super(PrivateClient, self).__init__(api_uri)
    self.auth = auth

  def _request(self, method, *relative_path_parts, **kwargs):
    """Sends an HTTP request to the REST API and receives the requested data.

    :param str method: HTTP method name
    :param relative_path_parts: the relative paths for the request URI
    :param kwargs: argument keywords
    :returns: requested data
    :raises APIError: for non-2xx responses

    """
    uri = self._create_api_uri(*relative_path_parts)
    response = get(uri, auth=self.auth, params=kwargs.get('params', None))
    return self._handle_response(response).json()

  def list_accounts(self):
    """`<https://docs.exchange.coinbase.com/#selecting-a-timestamp>`_"""
    return self._get('accounts')

  def get_account(self, account_id):
    """`<https://docs.exchange.coinbase.com/#get-an-account>`_"""
    return self._get('accounts', account_id)

  def get_account_history(self, account_id):
    """`<https://docs.exchange.coinbase.com/#get-account-history>`_"""
    return self._get('accounts', account_id, 'ledger')

class PrivatePaginationClient(PaginationClient):
  def __init__(self, auth, api_uri=None, before=True, limit=None, cursor=None):
    super(PrivatePaginationClient, self).__init__(api_uri,
                                                  before,
                                                  limit,
                                                  cursor)
    self.auth = auth

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
    response = get(uri, auth=self.auth, params=self._get_params(**kwargs))
    self.is_initial = False
    self.before_cursor = response.headers.get('cb-before', None)
    self.after_cursor = response.headers.get('cb-after', None)
    return self._handle_response(response).json()

class GetAccountHistoryPagination(PrivatePaginationClient):
  """`<https://docs.exchange.coinbase.com/#get-account-history>`_"""
  def __init__(self,
               account_id,
               auth,
               api_uri=None,
               before=True,
               limit=None,
               cursor=None):
    super(GetAccountHistoryPagination, self).__init__(auth,
                                                      api_uri,
                                                      before,
                                                      limit,
                                                      cursor)
    self.account_id = account_id

  def endpoint(self):
    if self._check_next():
      return self._get('accounts', self.account_id, 'ledger')
    else:
      return None

# TODO - ALL LIST RETURNS SUPPORT PAGINATION SO CREATE A PAGINATION CLIENT FOR EACH
