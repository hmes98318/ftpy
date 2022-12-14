# Logistics-Station

<a href="https://www.python.org/downloads/release/python-3109/"><img alt="Python 3.10" src="https://img.shields.io/badge/python-3.10-blue?style=for-the-badge&logo=PYTHON"></a>
<a href="https://github.com/hmes98318/Logistics-Station/blob/main/LICENSE"><img alt="GitHub" src="https://img.shields.io/github/license/hmes98318/Logistics-Station?style=for-the-badge"></a>    


A simple file shares implement in Python TCP socket.  

Using a centralized Server to send and receive files that multiple Client can transfer files to each other.  
Others can download the corresponding file from the Server by using the **pickup code** when the user upload the file to the Server and share the **pickup code** with them.  

TCP/IP network programming class final report.  

<img src="./public/Recv4.png" alt="Recv4" width="600"/>

## Installation
### Install modules
[`requirements.txt`](./requirements.txt)
```
pip install -r requirements.txt
```

### Open The Directory
```
cd src/
```

### Entrypoint
```
python ./main.py
```


## Server Deployment Docs
[`./server/README.md`](./server/README.md)


## Structure
The main file structure of the Client
```
src
├── main.py (Entrypoint)
│
├── data
│   └── userData
│
├── gui
│   ├── images
│   │   └── (UI images)
│   ├── LoginWindow.py (Login UI)
│   ├── MainWindow.py  (Main UI)
│   └── controller.py  (UI controller)
│
└── tcp
    └── Client.py
```
The main file structure of the Server
```
src
├── database
│   └── mongo.py
│
└── Server.py
```


## Examples
 * `account` : user  
 * `password` : password  
</br>
<img src="./public/login.png" alt="login" width="600"/>
<img src="./public/Recv.png" alt="Recv" width="600"/>
<img src="./public/Recv2.png" alt="Recv2" width="600"/>
<img src="./public/Recv3.png" alt="Recv3" width="600"/>
<img src="./public/Recv4.png" alt="Recv4" width="600"/>
<img src="./public/Send.png" alt="Send" width="600"/>
<img src="./public/Send2.png" alt="Send2" width="600"/>
<img src="./public/Send3.png" alt="Send3" width="600"/>
<img src="./public/Setting.png" alt="Setting" width="600"/>


## Copyright & License
The project is released under the GNU General Public License v3.0, see the [LICENCE](./LICENSE) file for details.  

Copyright (C) 2022-2023  [hmes98318](https://github.com/hmes98318) ,  [sakura0711](https://github.com/sakura0711)  
