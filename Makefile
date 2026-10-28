USER := NHKUser
ADMIN := Administrator
HOME_DIR := /Users/$(USER)
VENV := ~/Scripts/venv
PYTHON := python3.14
SERVICE := tv.newhopechurch.dmxpy
SERIAL := EN371065
PLIST := $(SERVICE).plist
PRO := false

all: install-service install-editor install-dmxpy install-pips install-libusb

install: all

install-homebrew:
	su - $(ADMIN) -c '/bin/bash -c "$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
	echo >> /Users/$(ADMIN)/.bash_profile
	echo 'eval "$(/opt/homebrew/bin/brew shellenv bash)"' >> /Users/$(ADMIN)/.bash_profile
	eval "$(/opt/homebrew/bin/brew shellenv bash)"

install-libusb: install-homebrew
	su - $(ADMIN) -c 'brew install libusb'

install-python314: install-homebrew
	su - $(ADMIN) -c 'brew install python@3.14'

clean:
	rm -f $(SERVICE) $(PLIST)

install-service: $(PLIST)
	mkdir -p ~/Library/LaunchAgents
	install $(PLIST) ~/Library/LaunchAgents

$(SERVICE): Services/macOS/$(SERVICE)
	sed -e "s#HOME#$(HOME_DIR)#g" -e "s#SERIAL#$(SERIAL)#g" $^ > $(SERVICE)

$(PLIST): $(SERVICE)
ifeq ($(PRO), false)
	sed -i.plist '/-p/d' $(SERVICE)
else
	cp $(SERVICE) $(PLIST)
endif

install-editor: editor.py
	mkdir -p ~/Applications
	install editor.py ~/Applications/editor.py

install-dmxpy: dmxpy.py
	mkdir -p ~/Scripts
	install dmxpy.py ~/Scripts/dmxpy.py

install-pips: venv
	$(VENV)/bin/$(PYTHON) -m pip install pyftdi
	$(VENV)/bin/$(PYTHON) -m pip install pyusb

venv: install-python314
	mkdir -p ~/Scripts
	$(PYTHON) -m venv $(VENV)

.PHONY: install-service install-editor install-dmxpy install-pips venv
