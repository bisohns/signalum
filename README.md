<p align="center">
  <img width="100" height="100" src="signalum.png"><br>
    <span> <a href="https://travis-ci.com/bisoncorps/signalum"><img src="https://travis-ci.com/bisoncorps/signalum.svg" alt="Build Status" height="18"></a> <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" height="18"></a> <a href="https://badge.fury.io/py/signalum"><img src="https://badge.fury.io/py/Signalum.svg" alt="PyPI version" height="18"></a> </span>
  <h1> Signalum </h1>
</p>

A Linux Package to detect and analyze existing connections from wifi and bluetooth. Also checkout the [Desktop Application](https://github.com/bisoncorps/signalum-desktop).

- [Signalum](#signalum)
  - [Installation](#installation)
  - [Development](#development)
  - [Usage](#usage)
  - [Contribution](#contribution)
  - [License (MIT)](#license-mit)

## Installation

```bash
    pip install signalum
```

## Development

```bash
    git clone git@github.com:bisoncorps/signalum.git

    sudo apt-get install bluetooth libbluetooth-dev
    
    cd signalum

    pip install -r requirements.txt
```



## Usage

```python
   from signalum.core import _bluetooth as bt
   from signalum.core import _wifi as wf

   kwargs = dict()
   # avoid showing graph when calling from code
   kwargs['graph'] = False
   kwargs['color'] = False
   kwargs['analyze_all'] = True
   # no extra info
   kwargs['show_extra_info'] = True
   wf_devices = wf.wifilyze(**kwargs)
   # contains two lists, first is the list of cell objects
   # print all properties of first Cell object
   print(wf_devices[0][0].__dict__)
   # {'ssid': 'Dexter', 
   # ... ,
   #   'address': '***********', 
   #   'encrypted': True, 
   #   'encryption_type': 'wpa2', 
   #   'signal': -33,}   

   # show device names 
   kwargs['show_names'] = True
   kwargs['show_extra_info']
   bt_devices = bt.bluelyze(**kwargs)
   print(bt_devices[0][0])
   # ['Deven-Dexter', '***********', -59, 'Phone', 'Smartphone', 'Rendering|Object Transfer|Audio|Information|']

```

Signalum also comes with a cli tool called `signalyze`
![Demo](output.gif)

```bash
  ▄▄▄▄    ▄                         ▀▀█           ▄▄▄▄▄▄
 █▀   ▀   █     ▄▄▄▄  ▄ ▄▄    ▄▄▄     █    ▄   ▄      █▀  ▄▄▄
 ▀█▄▄▄    █    █▀ ▀█  █▀  █  ▀   █    █    ▀▄ ▄▀    ▄█   █▀  █
     ▀█   ▀    █   █  █   █  ▄▀▀▀█    █     █▄█    ▄▀    █▀▀▀▀
 ▀▄▄▄█▀   █    ▀█▄▀█  █   █  ▀▄▄▀█    ▀▄▄   ▀█    ██▄▄▄▄ ▀█▄▄▀
                ▄  █                        ▄▀
                 ▀▀                        ▀▀
                 ▀▀                        ▀▀
usage: signalyze [-h] [-o OUTPUT] [--show-name] [-b | -w | -all] [--show-graph | --show-extra-info]
optional arguments:
    -h, --help            show this help message and exit                  
    -o OUTPUT, --output OUTPUT  save to an output csv file                       
    --show-name           Show Device name and mac address                 
    -b, --bluetooth       Analyze only bluetooth                           
    -w, --wifi            Analyze only wifi                                
    -all, --analyze-all   Analyze both wifi and bluetooth  
    --show-graph          Show Realtime graph of nearby devices
    --show-extra-info     Show extra information like services and device  classification   
```


## Contribution

You are very welcome to modify and use them in your own projects.

## License (MIT)

This project is opened under the [MIT 2.0 License](https://github.com/bisoncorps/signalum/blob/master/LICENSE) which allows very broad use for both academic and commercial purposes.
