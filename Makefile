USER := NHKUser
HOME_DIR := /Users/$(USER)
VENV := ~/Scripts/venv
PYTHON := python3.14

all: install-service install-editor install-dmxpy install-pips

install-service: tv.newhopechurch.dmxpy.plist
	mkdir -p ~/Library/LaunchAgents
	install $^ ~/Library/LaunchAgents

tv.newhopechurch.dmxpy.plist: Services/macOS/tv.newhopechurch.dmxpy
	sed "s#HOME#$(HOME_DIR)#g" $^ > tv.newhopechurch.dmxpy.plist

install-editor: editor.py
	mkdir -p ~/Applications
	install editor.py ~/Applications/editor.py

install-dmxpy: dmxpy.py
	mkdir -p ~/Scripts
	install dmxpy.py ~/Scripts/dmxpy.py

install-pips: venv
	$(VENV)/bin/$(PYTHON) -m pip install pyftdi
	$(VENV)/bin/$(PYTHON) -m pip install pyusb

venv:
	mkdir -p ~/Scripts
	$(PYTHON) -m venv $(VENV)

.PHONY: install-service install-editor install-dmxpy install-pips venv
