"""The websocket feed provides real-time updates on orders and trades. These
updates can be applied on to a level 2 or 3 order book snapshot to maintain an 
accurate and up-to-date copy of the exchange order book.

Find more here: `<https://docs.exchange.coinbase.com/#real-time-order-book>`_

.. module:: orderbook
   :synopsis: Real-Time Order Book

.. moduleauthor:: Alexander Simeonov <agsimeon@buffalo.edu>

"""
from json import dumps
from threading import Thread
from time import sleep

from cbexchange.market import MarketClient
from cbexchange.websock import WSClient


class OrderBook(object):
  """`<https://docs.exchange.coinbase.com/#real-time-order-book>`_

  Includes a real-time thread that makes sure the order book is up to date.
  Supports the 'with' statment.

  The order book format will be:

  >>> {
  >>>    "asks": {
  >>>      "da863862-25f4-4868-ac41-005d11ab0a5f": {
  >>>        "price": "295.97",
  >>>        "size": "5.72036512"
  >>>      },
  >>>      ...
  >>>    },
  >>>    "bids": {
  >>>      "3b0f1225-7f84-490b-a29f-0faef9de823a": {
  >>>        "price": "295.96",
  >>>        "size": "0.05088265"
  >>>      },
  >>>      ...
  >>>    },
  >>>    "sequence": 3
  >>> }

  :param str ws_uri:  WebSocket URI.
  :param str api_url:  Coinbase Exchange REST API URI.
  :param str product_id: the product of interest

  """
  WS_URI = 'wss://ws-feed.exchange.coinbase.com'
  API_URI = 'https://api.exchange.coinbase.com'
  PRODUCT_ID = 'BTC-USD'

  def __init__(self, ws_uri=None, api_uri=None, product_id=None):
    self.API_URI = api_uri or self.API_URI
    self.WS_URI = ws_uri or self.WS_URI
    self.PRODUCT_ID = product_id or self.PRODUCT_ID
    self.ws_client = WSClient(ws_uri=self.WS_URI, ws_product_id=self.PRODUCT_ID)
    self.ws_client.connect()
    client = MarketClient(api_uri=self.API_URI)
    self.book = client.get_product_order_book(3, self.PRODUCT_ID)
    self.sequence = self.book['sequence']
    self.die = False
    self.pause = False

    asks = {}
    for entry in self.book['asks']:
      asks[entry[2]] = {'price':entry[0], 'size':entry[1]}
    self.book['asks'] = asks

    bids = {}
    for entry in self.book['bids']:
      bids[entry[2]] = {'price':entry[0], 'size':entry[1]}
    self.book['bids'] = bids

    Thread(target=self._real_time_thread, args=[]).start()

  def _get_key(self, message):
    if message['side'] == 'buy':
      return 'bids'
    else:
      return 'asks'

  def _get_order_id(self, message):
    return message['order_id']

  def _handle_open(self, message):
    key = self._get_key(message)
    self.book[key][self._get_order_id(message)] = {
      'price':message['price'],
      'size':message['remaining_size']
    }

  def _handle_match(self, message):
    maker = message['maker_order_id']
    key = self._get_key(message)
    if maker in self.book[key]:
      left = float(self.book[key][maker]['size'])
      right = float(message['size'])
      self.book[key][maker]['size'] = str(left - right)

  def _handle_done(self, message):
    if message['order_type'] == 'market':
      return
    key = self._get_key(message)
    self.book[key].pop(self._get_order_id(message), None)

  def _handle_change(self, message):
    if message['price'] is None: # market
      return
    if 'new_funds' in message:   # market
      return
    key = self._get_key(message)
    order_id = self._get_order_id(message)
    if order_id in self.book[key]:
      self.book[key][order_id]['size'] = message['remaining_size']

  def _real_time_thread(self):
    """Handles real-time updates to the order book."""
    while self.ws_client.connected():
      if self.die:
        break
      
      if self.pause:
        sleep(5)
        continue

      message = self.ws_client.receive()

      if message is None:
        break

      message_type = message['type']

      if message_type  == 'error':
        continue
      if message['sequence'] <= self.sequence:
        continue

      if message_type == 'open':
        self._handle_open(message)
      elif message_type == 'match':
        self._handle_match(message)
      elif message_type == 'done':
        self._handle_done(message)
      elif message_type == 'change':
        self._handle_change(message)
      else:
        continue

    self.ws_client.disconnect()

  def __enter__(self):
    return self
  
  def __exit__(self, type, value, traceback):
    self.end()

  def __str__(self):
    if self.book:
      return dumps(self.book, indent=2, sort_keys=True)
    else:
      return str(self.book)

  def end(self):
    """Makes sure the real-time thread dies and the WebSocket disconnects."""
    self.die = True

  def pause(self):
    """Stops real-time updates until resume is called."""
    self.pause = True
  
  def resume(self):
    """Resumes real-time updates."""
    self.pause = False

  def get_order_book(self):
    """Returns the Real-Time Order Book.

    :returns: the Real-Time Order Book
    :rtype: dict

    """
    return self.book
