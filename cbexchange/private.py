"""Private endpoints are available for order management, and account management.
Every private request must be signed using the described authentication scheme.

Find more here: `<https://docs.exchange.coinbase.com/#private>`_

.. module:: private
   :synopsis: Private API

.. moduleauthor:: Alexander Simeonov <agsimeon@buffalo.edu>

"""
from base64 import b64decode
from hashlib import sha256
from hmac import new
from time import time

from requests import delete, get, post
from requests.auth import AuthBase

from cbexchange.client import RESTClient, PaginationClient

# List Orders Status
STATUS_ALL     = 'all'
STATUS_OPEN    = 'open'
STATUS_PENDING = 'pending'



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
    if method == 'get':
      response = get(uri, auth=self.auth, params=kwargs.get('params', None))
    elif method == 'post':
      response = post(uri, auth=self.auth, json=kwargs.get('data', None))
    else:
      response = delete(uri, auth=self.auth, json=kwargs.get('data', None))
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

  def get_holds(self, account_id):
    """`<https://docs.exchange.coinbase.com/#get-holds>`_"""
    return self._get('accounts', account_id, 'holds')

  def _place_order(self,
                   side,
                   product_id='BTC-USD',
                   client_oid=None,
                   type=None,
                   stp=None,
                   price=None,
                   size=None,
                   funds=None,
                   time_in_force=None,
                   cancel_after=None,
                   post_only=None):
    """`<https://docs.exchange.coinbase.com/#orders>`_"""
    data = {
      'side':side,
      'product_id':product_id,
      'client_oid':client_oid,
      'type':type,
      'stp':stp,
      'price':price,
      'size':size,
      'funds':funds,
      'time_in_force':time_in_force,
      'cancel_after':cancel_after,
      'post_only':post_only
    }
    return self._post('orders', data=data)

  def place_limit_order(self,
                        side,
                        price,
                        size,
                        product_id='BTC-USD',
                        client_oid=None,
                        stp=None,
                        time_in_force=None,
                        cancel_after=None,
                        post_only=None):
    """`<https://docs.exchange.coinbase.com/#orders>`_"""
    return self._place_order(side,
                             product_id=product_id,
                             client_oid=client_oid,
                             type='limit',
                             stp=stp,
                             price=price,
                             size=size,
                             time_in_force=time_in_force,
                             cancel_after=cancel_after,
                             post_only=post_only)

  def place_market_order(self,
                         side,
                         product_id='BTC-USD',
                         size=None,
                         funds=None,
                         client_oid=None,
                         stp=None):
    """`<https://docs.exchange.coinbase.com/#orders>`_"""
    return self._place_order(type='market',
                             side=size,
                             product_id=product_id,
                             size=size,
                             funds=funds,
                             client_oid=client_oid,
                             stp=stp)

  def cancel_order(self, order_id):
    """`<https://docs.exchange.coinbase.com/#cancel-an-order>`_"""
    return self._delete('orders', order_id)

  def cancel_all(self, product_id=None):
    """`<https://docs.exchange.coinbase.com/#cancel-all>`_"""
    return self._delete('orders', data={'product_id':product_id})

  def list_orders(self, status=None):
    """`<https://docs.exchange.coinbase.com/#list-orders>`_"""
    return self._get('orders', params={'status':status})

  def get_order(self, order_id):
    """`<https://docs.exchange.coinbase.com/#get-an-order>`_"""
    return self._get('orders', order_id)

  def list_fills(self):
    """`<https://docs.exchange.coinbase.com/#list-fills>`_"""
    return self._get('fills')

  def _deposit_withdraw(self, type, amount, coinbase_account_id):
    """`<https://docs.exchange.coinbase.com/#depositwithdraw>`_"""
    data = {
      'type':type,
      'amount':amount,
      'coinbase_account_id':coinbase_account_id
    }
    return self._post('transfers', data=data)

  def deposit(self, amount, coinbase_account_id):
    """`<https://docs.exchange.coinbase.com/#depositwithdraw>`_"""
    return self._deposit_withdraw('deposit', amount, coinbase_account_id)

  def withdraw(self, amount, coinbase_account_id):
    """`<https://docs.exchange.coinbase.com/#depositwithdraw>`_"""
    return self._deposit_withdraw('withdraw', amount, coinbase_account_id)

  def _new_report(self,
                  type,
                  start_date,
                  end_date,
                  product_id='BTC-USD',
                  account_id=None,
                  format=None,
                  email=None):
    """`<https://docs.exchange.coinbase.com/#create-a-new-report>`_"""
    data = {
      'type':type,
      'start_date':self._format_iso_time(start_date),
      'end_date':self._format_iso_time(end_date),
      'product_id':product_id,
      'account_id':account_id,
      'format':format,
      'email':email
    }
    return self._post('reports', data=data)

  def new_fills_report(self,
                       start_date,
                       end_date,
                       account_id=None,
                       product_id='BTC-USD',
                       format=None,
                       email=None):
    """`<https://docs.exchange.coinbase.com/#create-a-new-report>`_"""
    return self._new_report(start_date,
                            'fills',
                            end_date,
                            account_id,
                            product_id,
                            format,
                            email)

  def new_accounts_report(self,
                          start_date,
                          end_date,
                          account_id,
                          product_id='BTC-USD',
                          format=None,
                          email=None):
    """`<https://docs.exchange.coinbase.com/#create-a-new-report>`_"""
    return self._new_report(start_date,
                            'account',
                            end_date,
                            product_id,
                            account_id,
                            format,
                            email)

  def get_report_status(self, report_id):
    """`<https://docs.exchange.coinbase.com/#get-report-status>`_"""
    return self._get('reports', report_id)

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
    if method == 'get':
      response = get(uri, auth=self.auth, params=kwargs.get('params', None))
    elif method == 'post':
      response = post(uri, auth=self.auth, json=kwargs.get('data', None))
    else:
      response = delete(uri, auth=self.auth, json=kwargs.get('data', None))
    self.is_initial = False
    self.before_cursor = response.headers.get('cb-before', None)
    self.after_cursor = response.headers.get('cb-after', None)
    return self._handle_response(response).json()

class ListAccountsPagination(PrivatePaginationClient):
  """`<https://docs.exchange.coinbase.com/#selecting-a-timestamp>`_"""
  def endpoint(self):
    if self._check_next():
      return self._get('accounts')
    else:
      return None

class AccountPagination(PrivatePaginationClient):
  def __init__(self,
               account_id,
               auth,
               api_uri=None,
               before=True,
               limit=None,
               cursor=None):
    super(AccountPagination, self).__init__(auth,
                                            api_uri,
                                            before,
                                            limit,
                                            cursor)
    self.account_id = account_id

class GetAccountHistoryPagination(AccountPagination):
  """`<https://docs.exchange.coinbase.com/#get-account-history>`_"""
  def endpoint(self):
    if self._check_next():
      return self._get('accounts', self.account_id, 'ledger')
    else:
      return None

class GetHoldsPagination(AccountPagination):
  """`<https://docs.exchange.coinbase.com/#get-holds>`_"""
  def endpoint(self):
    if self._check_next():
      return self._get('accounts', self.account_id, 'holds')
    else:
      return None

class ListFillsPagination(PrivatePaginationClient):
  """`<https://docs.exchange.coinbase.com/#list-fills>`_"""
  def endpoint(self):
    if self._check_next():
      return self._get('fills')
    else:
      return None

class CancelAllPagination(PrivatePaginationClient):
  """`<https://docs.exchange.coinbase.com/#cancel-all>`_"""
  def __init__(self,
               product_id,
               auth,
               api_uri=None,
               before=True,
               limit=None,
               cursor=None):
    super(AccountPagination, self).__init__(auth,
                                            api_uri,
                                            before,
                                            limit,
                                            cursor)
    self.product_id = product_id

  def endpoint(self):
    if self._check_next():
      return self._delete('orders', data={'product_id':self.product_id})
    else:
      return None

class ListOrdersPagination(PrivatePaginationClient):
  """`<https://docs.exchange.coinbase.com/#list-orders>`_"""
  def __init__(self,
               auth,
               status=None,
               api_uri=None,
               before=True,
               limit=None,
               cursor=None):
    super(ListOrdersPagination, self).__init__(auth,
                                               api_uri,
                                               before,
                                               limit,
                                               cursor)
    self.status = status

  def endpoint(self):
    if self._check_next():
      return self._get('orders', params={'status':self.status})
    else:
      return None
