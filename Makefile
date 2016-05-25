.PHONY: clean release

unexport LANG
unexport LC_ADDRESS
unexport LC_COLLATE
unexport LC_CTYPE
unexport LC_IDENTIFICATION
unexport LC_MEASUREMENT
unexport LC_MESSAGES
unexport LC_MONETARY
unexport LC_NAME
unexport LC_NUMERIC
unexport LC_PAPER
unexport LC_TELEPHONE
unexport LC_TIME

test_sdist:
	@python setup.py sdist

release_sdist:
ifeq ($(VERSION),)
	$(error VERSION must be set to build a release and deploy this package)
endif
ifeq ($(RELEASE_GPG_KEYNAME),)
	$(error RELEASE_GPG_KEYNAME must be set to build a release and deploy this package)
endif
	@echo "==> Python tagging version $(VERSION)"
	@echo "__version__=\"$(VERSION)\"" > helium/version.py
	@bash ./scripts/publish.sh $(VERSION) validate
	@git tag --sign -a "$(VERSION)" -m "helium-commander $(VERSION)" --local-user "$(RELEASE_GPG_KEYNAME)"
	@git push --tags
	@echo "==> Python (sdist release)"
	@python setup.py sdist upload -s -i $(RELEASE_GPG_KEYNAME)
	@bash ./scripts/publish.sh $(VERSION)

release: release_sdist
ifeq ($(RELEASE_GPG_KEYNAME),)
	$(error RELEASE_GPG_KEYNAME must be set to build a release and deploy this package)
endif
	@echo "==> Python 2.7 (release)"
	@python2.7 setup.py build --build-base=py-build/2.7 bdist_wheel upload -s -i $(RELEASE_GPG_KEYNAME)


clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	rm -rf ./dist ./py-build
