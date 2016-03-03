"""The WebSocket Feed provides real-time market data updates for orders and
trades. 
   
Find more here: `<https://docs.exchange.coinbase.com/#websocket-feed>`_

.. module:: websock
   :synopsis: WebSocket Feed

.. moduleauthor:: Alexander Simeonov <agsimeon@buffalo.edu>

"""
from json import dumps, loads
from threading import Lock, Thread
from time import sleep

from websocket import create_connection

from cbexchange.client import APIClient


class WSClient(APIClient):
  """API Client for Coinbase Exchange WebSocket Feed.

  This class starts in a disconnected state so make sure to connect before
  attempting to receive any messages.  When using the 'with' statement the
  client connects and disconnects automatically.

  Once connected the client starts a thread which keeps the WebSocket alive 
  using periodic pings. There will be only one keep alive thread per client
  instance. If the WebSocket connection is somehow lost, the keep alive thread 
  will clean up and exit.

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
  :param str ws_type: `<https://docs.exchange.coinbase.com/#subscribe>`_
  :param str ws_product_id: `<https://docs.exchange.coinbase.com/#subscribe>`_

  """
  WS_URI = 'wss://ws-feed.exchange.coinbase.com'
  WS_TYPE = 'subscribe'
  WS_PRODUCT_ID = 'BTC-USD'

  def __init__(self, ws_uri=None, ws_type=None, ws_product_id=None):
    self.WS_URI = ws_uri or self.WS_URI
    self.WS_TYPE = ws_type or self.WS_TYPE
    self.WS_PRODUCT_ID = ws_product_id or self.WS_PRODUCT_ID
    self._ws = None
    self._thread = None
    self._lock = Lock()

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

  def _format_message(self, message):
    """Makes sure messages are Pythonic.

    :param str message: raw message
    :returns: Pythonic message
    :rtype: dict

    """
    return loads(message)

  def _keep_alive_thread(self):
    """Used exclusively as a thread which keeps the WebSocket alive."""
    while True:
      with self._lock:
        if self.connected():
          self._ws.ping()
        else:
          self.disconnect()
          self._thread = None
          return
      sleep(30)

  def connect(self):
    """Connects and subscribes to the WebSocket Feed."""
    if not self.connected():
      self._ws = create_connection(self.WS_URI)
      message = {
        'type':self.WS_TYPE,
        'product_id':self.WS_PRODUCT_ID
      }
      self._ws.send(dumps(message))

      # There will be only one keep alive thread per client instance
      with self._lock:
        if not self._thread:
          thread = Thread(target=self._keep_alive_thread, args=[])
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
