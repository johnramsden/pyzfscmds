install:
	test -d `git rev-parse --show-toplevel`/.git && git pull || true
	python3.6 -m ensurepip
	cd `git rev-parse --show-toplevel` && python3.6 setup.py install

uninstall:
	python3.6 -m pip uninstall -y pyzfscmds

help:
	@echo "    install"
	@echo "        Installs pyzfscmds."
	@echo "    uninstall"
	@echo "        Removes pyzfscmds."
