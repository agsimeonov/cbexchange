"""The WebSocket Feed provides real-time market data updates for orders and
   trades. Find more here: https://docs.exchange.coinbase.com/#websocket-feed

.. module:: websock
   :synopsis: Websocket Feed

.. moduleauthor:: Alexander Simeonov <agsimeon@buffalo.edu>

"""
from datetime import datetime
from json import dumps, loads
from threading import current_thread, Thread
from time import sleep

from websocket import create_connection


class WSClient(object):
  """API Client for Coinbase Exchange WebSocket Feed.

  This class starts in a disconnected state so make sure to connect before
  attempting to receive any messages.  When using the 'with' statement the
  client connects and disconnects automatically.

  Once connected the client starts a daemon thread which keeps the WebSocket 
  alive using periodic pings. If the parent thread of the daemon dies or the 
  WebSocket connection is somehow lost, the daemon will clean up and exit.

  The client is iterable over the messages in the feed:

  :Example:

  >>> from cbexchange.websock import WSClient
  >>> client = WSClient()
  >>> client.connect()
  >>> for message in client:
  >>>   print(message)

  The client supports the 'with' statment:

  :Example:

  >>> from cbexchange.websock import WSClient
  >>> with WSClient() as client:
  >>>   print(client.receive())

  :param str ws_uri:  WebSocket URI.
  :param str ws_type: https://docs.exchange.coinbase.com/#subscribe
  :param str ws_product_id: https://docs.exchange.coinbase.com/#subscribe

  """
  WS_URI = 'wss://ws-feed.exchange.coinbase.com'
  WS_TYPE = 'subscribe'
  WS_PRODUCT_ID = 'BTC-USD'

  _ws = None

  def __init__(self, ws_uri=None, ws_type=None, ws_product_id=None):
    self.WS_URI = ws_uri or self.WS_URI
    self.WS_TYPE = ws_type or self.WS_TYPE
    self.WS_PRODUCT_ID = ws_product_id or self.WS_PRODUCT_ID

  def __iter__(self):
    return self

  def __enter__(self):
    self.connect()
    return self

  def __exit__(self, type, value, traceback):
    self.disconnect()

  def __next__(self):
    """Iterator function for Python 3.

    :returns: the next message in the sequence
    :rtype: dict
    :raises StopIteration: if the WebSocket is not connected

    """
    next = self.receive()
    if next:
      return next
    raise StopIteration

  # Iterator function for Python 2.
  next = __next__

  def _to_float(self, message, key):
    """Converts a value in the message to float.

    :param dict message: the input message
    :param str key: associated value will be converted to float
      
    """
    message[key] = float(message[key])

  def _format_message(self, message):
    """Makes sure messages are Pythonic.

    :param str message: raw message
    :returns: Pythonic message
    :rtype: dict

    """
    message = loads(message)

    if message['type'] == 'received':
      if message['order_type'] == 'limit':
        self._to_float(message, 'size')
        self._to_float(message, 'price')
      else:
        if 'funds' in message:
          self._to_float(message, 'funds')
    elif message['type'] == 'open':
      self._to_float(message, 'price')
      self._to_float(message, 'remaining_size')
    elif message['type'] == 'done':
      if message['order_type'] == 'limit':
        self._to_float(message, 'price')
        self._to_float(message, 'remaining_size')
    elif message['type'] == 'match':
      self._to_float(message, 'size')
      self._to_float(message, 'price')
    elif message['type'] == 'change':
      if message['price']:
        self._to_float(message, 'price')
      if 'new_size' in message:
        self._to_float(message, 'new_size')
        self._to_float(message, 'old_size')
      else:
        self._to_float(message, 'new_funds')
        self._to_float(message, 'old_funds')
    else:
      return message

    message['time'] = datetime.strptime(message['time'],
                                        '%Y-%m-%dT%H:%M:%S.%fZ')

    return message

  def _keep_alive_thread(self, parent_thread):
    """Used exclusively as a thread which keeps the WebSocket alive.

    :param threading.Thread parent_thread: the parent thread

    """
    while(parent_thread.is_alive()):
      if self.connected():
        self._ws.ping()
        sleep(30)
      else:
        break

    if self.connected():
      self.disconnect()

  def connect(self):
    """Connects and subscribes to the WebSocket Feed."""
    if not self.connected():
      self._ws = create_connection(self.WS_URI)
      message = {
        'type':self.WS_TYPE,
        'product_id':self.WS_PRODUCT_ID
      }
      self._ws.send(dumps(message))
      thread = Thread(target=self._keep_alive_thread, args=[current_thread()])
      thread.daemon = True
      thread.start()

  def disconnect(self):
    """Disconnects from the WebSocket Feed."""
    if self.connected():
      self._ws.close()
      self._ws = None

  def receive(self):
    """Receive the next message in the sequence.

    :returns: the next message in the sequence, None if not connected
    :rtype: dict

    """
    if self.connected():
      return self._format_message(self._ws.recv())
    return None

  def connected(self):
    """Checks if we are connected to the WebSocket Feed.

    :returns: True if connected, otherwise False
    :rtype: bool

    """
    if self._ws:
      return self._ws.connected
    return False
