from distutils.core import setup
setup(
  name = 'cbexchange',
  packages = ['cbexchange'],
  version = '1.0.1',
  description = 'CBExchange - Coinbase Exchange Python API',
  author = 'Alexander Simeonov',
  author_email = 'agsimeon@buffalo.edu',
  url = 'https://github.com/agsimeonov/cbexchange',
  download_url = 'https://github.com/agsimeonov/cbexchange/tarball/1.0.0',
  keywords = ['cbexchange',
              'coinbase',
              'api',
              'bitcoin',
              'client',
              'exchange',
              'websocket',
              'orderbook',
              'order',
              'book'],
  install_requires=[
    'requests',
    'websocket-client'
  ],
  classifiers = [],
)