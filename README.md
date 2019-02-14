# MultiProtocol Wireless Detection

Package to detect existing connections from wifi, bluetooth and zigbee

[![Build Status](https://travis-ci.org/bisoncorps/multiprotocol_wireless_detection.svg?branch=master)](https://travis-ci.com/bisoncorps/multiprotocol_wireless_detection) [![PyPI version](https://badge.fury.io/py/MultiProWireless.svg)](https://badge.fury.io/py/MultiProWireless)

- [MultiProtocol Wireless Detection](#multiprotocol-wireless-detection)
  - [Installation](#installation)
  - [Development](#development)
  - [Documentation](#documentation)
  - [Running the tests](#running-the-tests)
  - [Usage](#usage)
  - [Contribution](#contribution)
  - [License (MIT)](#license-mit)

## Installation

```bash
    pip install multiprowireless
```

## Development

```bash
    git clone git@github.com:bisoncorps/multiprotocol_wireless_detection.git

    # for linux bluetooth
    sudo apt-get install bluetooth libbluetooth-dev

    pip install pipenv

    pipenv install
```

## Documentation

[Github Pages](https://bisoncorps.github.io/multiprotocol_wireless_detection)

## Running the tests

```bash
    cd multiprotocol_wireless_detection/multiprowireless/
```

```bash
    python tests/__init__.py
```

## Usage

```python
    from multiprowireless import scanner

```

## Contribution

You are very welcome to modify and use them in your own projects.

Please keep a link to the [original repository](https://github.com/bisoncorps/multiprotocol_wireless_detection). If you have made a fork with substantial modifications that you feel may be useful, then please [open a new issue on GitHub](https://github.com/bisoncorps/multiprotocol_wireless_detection/issues) with a link and short description.

## License (MIT)

This project is opened under the [MIT 2.0 License](https://github.com/bisoncorps/multiprotocol_wireless_detection/blob/master/LICENSE) which allows very broad use for both academic and commercial purposes.
