# Zenmap Alpine

A lightweight GTK3 graphical frontend for Nmap, designed for Alpine Linux.

## Features

- GTK3 graphical interface
- Nmap target input
- Ping Scan
- Quick Scan
- Regular Scan
- Service Detection
- OS Detection
- Full TCP Scan
- Live Nmap output
- Stop running scans
- Save scan results to a text file
- No AI
- No cloud service
- No internet connection required by the GUI itself

## Requirements

- Alpine Linux
- Python 3
- GTK3
- PyGObject
- Nmap
- An active graphical XFCE/X11 session

## Installation

Install the dependencies:

```sh
apk add python3 py3-gobject3 gtk+3.0 nmap
