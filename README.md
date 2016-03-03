# CBExchange - Coinbase Exchange Python API

Currently this is the only Python implementation of the Coinbase Exchange API that has full coverage.

CBExchange has full support for:
* Private API
* Market Data (Public) API
* WebSocket Feed
* Pagination
* Errors

### Compatibility
The Library has been fully tested on Python 2.7 however it has been written with Python 3 compatibility in mind so it should have no problems as 2to3 tests pass for all modules.

### Requirements
You need to have requests and and websocket-client on your system:

```
pip install requests
pip install websocket-client
```

### Installation
You can simply run the following command to install CBExchange:

```
pip install cbexchange
```

CBExchange PyPI site: https://pypi.python.org/pypi/cbexchange

### Documentation
#### http://agsimeonov.github.io/cbexchange
Take advantage of the CBExchange documentation. It includes informations for all public modules, functions and parameters. As well as some examples.

### Bugs/Issues
Please create an issue in the issue tracker if you encounter any bugs/issues.  While I have tested most functionality I am yet to write a comprehensive test suite.
