
TOP=.

# the system python we will use for bootstrapping
SYS_PYTHON=python2.7

# requirements file
REQUIREMENTS_TXT=$(TOP)/requirements.txt

# cleanup some things after building...
POST_BUILD_CLEANUPS=\
        doc  man *~

PIP=$(TOP)/bin/pip
PIP_CACHE=$(TOP)/downloads
PIP_INSTALL_ARGS=--use-mirrors --download-cache $(PIP_CACHE)

# where the sources are and how to build them
PACKAGE_DIR=$(TOP)/candelabra
PACKAGE_TESTS_DIR=$(TOP)/tests
SETUP_PY=$(TOP)/setup.py

# the main script
MAIN_SCRIPT=$(TOP)/bin/candelabra
NOSE_SCRIPT=$(TOP)/bin/nosetests

# API docs dir
SPHINX=$(TOP)/bin/sphinx-build
API_GEN=$(TOP)/bin/sphinx-apidoc
API_DOCS_DIR=$(TOP)/docs/api/
API_DOCS_OUTPUT_DIR=$(TOP)/docs/api/build
API_DOCS_WEB_TEMP=$(TOP)/docs/web
API_DOCS_WEB_URL=https://github.com/inercia/candelabra.git

COVERAGE_DOCS_OUTPUT_DIR=$(TOP)/docs/coverage

# nose arguments
NOSE_ARGS=--with-xunit --all-modules

####################################################################################################

all: basic

$(PIP_CACHE):
	echo ">>> Creating downloads cache"
	mkdir -p $(PIP_CACHE)

$(PIP): $(PIP_CACHE)
	virtualenv .

basic: $(PIP) $(REQUIREMENTS_TXT) $(SETUP_PY)
	@echo
	@echo ">>> Installing BASIC packages with PIP..."
	$(PIP) install $(PIP_INSTALL_ARGS) -r $(REQUIREMENTS_TXT)
	@echo ">>> BASIC packages installed SUCCESSFUL!! (do a 'make devel' in devel machines)"

devel: basic
	@echo ">>> Installing DEVELOPMENT packages with PIP..."
	$(PIP) install $(PIP_INSTALL_ARGS) -e .[develop] -e .[tests]
	@echo ">>> DEVELOPMENT packages installed SUCCESSFUL !!"

$(MAIN_SCRIPT): devel

####################################################################################################
# cleanup

clean-pyc: 
	@echo ">>> Cleaning pyc..."
	rm -f     `find $(PACKAGE_DIR) $(PACKAGE_TESTS_DIR) -name '*.pyc'`
	rm -f     `find $(PACKAGE_DIR) $(PACKAGE_TESTS_DIR) -name '*.pyo'`

clean: clean-pyc
	@echo ">>> Cleaning stuff..."
	rm -rf    $(TOP)/bin $(TOP)/doc $(TOP)/dist $(TOP)/var
	rm -rf    $(TOP)/conf/*.conf  $(TOP)/conf/*/*.conf
	rm -rf    $(TOP)/*.spec $(TOP)/buildout/packaging/*.spec
	rm -rf    $(TOP)/develop-eggs $(TOP)/eggs $(TOP)/html
	rm -rf    $(TOP)/include $(TOP)/man $(TOP)/local $(TOP)/lib $(TOP)/logs $(TOP)/parts
	rm -rf    $(TOP)/run $(TOP)/share $(TOP)/sbin
	rm -rf    $(TOP)/doc $(TOP)/docs/coverage/*
	rm -rf    $(TOP)/build $(TOP)/local $(TOP)/temp $(TOP)/*_temp $(TOP)/*~  $(TOP)/pip-*
	rm -rf    $(TOP)/*.egg-info  $(TOP)/*/*.egg-info   $(TOP)/nosetests.xml
	rm -rf    $(TOP)/*__tmp  $(TOP)/*log.txt  $(TOP)/test.py*  $(TOP)/*.log  $(TOP)/log
	rm -rf    $(TOP)/.installed.cfg $(TOP)/depends-log.txt
	rm -rf    $(TOP)/coverage.xml
	rm -rf    $(TOP)/atlassian-ide-plugin.xml
	rm -rf    $(TOP)/*packages-log.txt $(TOP)/profile.* $(TOP)/*.log
	rm -rf    $(TOP)/nosetests.xml  $(TOP)/nosetests.log
	rm -rf    $(TOP)/*.rpm $(TOP)/*.deb $(TOP)/*.tgz $(TOP)/*.pdf $(TOP)/*.dump
	rm -rf    $(TOP)/.Python
	rm -rf    `find . -name '*.egg-info'`
	rm -rf    `find . -name '*.egg-lnk'`
	rm -rf    $(RPM_TAR)
	@echo ">>> Everything bright and clean!!"
	@echo ">>> You can now 'make'..."

distclean: clean-docs clean
	rm -rf $(PIP_CACHE)

####################################################################################################
# distribution

sdist:
	$(SYS_PYTHON) setup.py sdist

bdist:
	$(SYS_PYTHON) setup.py bdist

####################################################################################################
# documentation

# note: on Mac OS X, set "LC_ALL=en_US.UTF-8" and "LANG=en_US.UTF-8" for docs generation

.PHONY: docs docs-pdf 00-docs-run 00-docs-pdf-run 

clean-docs:
	@echo ">>> Cleaning docs..."
	rm -rf    $(API_DOCS_OUTPUT_DIR)

$(SPHINX): devel
$(API_GEN): $(SPHINX)

docs-api: $(API_GEN)
	@echo ">>> Creating API docs..."
	rm -f $(API_DOCS_DIR)/candelabra.*.rst
	ABS_PACKAGE_DIR=`pwd`/$(PACKAGE_DIR) ; \
	    $(API_GEN) --force -o $(API_DOCS_DIR) -d 8 -s rst  $$ABS_PACKAGE_DIR  \
	    `find $$ABS_PACKAGE_DIR -name tests`

00-docs-run: $(SPHINX) docs-api
	@echo ">>> Creating development docs..."
	@$(SPHINX) -q -b html  $(API_DOCS_DIR)  $(API_DOCS_OUTPUT_DIR)
	@echo ">>> Documentation left at $(API_DOCS_OUTPUT_DIR)/doc_index.html"

docs:     clean-docs all 00-docs-run

docs-web: docs
	rm -rf $(API_DOCS_WEB_TEMP)
	@echo ">>> Checking out repo..."
	git clone $(API_DOCS_WEB_URL)  $(API_DOCS_WEB_TEMP)
	@echo ">>> Switching to pages branch..."
	cd $(API_DOCS_WEB_TEMP) && git checkout gh-pages
	@echo ">>> Removing old pages..."
	rm -rf $(API_DOCS_WEB_TEMP)/*
	@echo ">>> Copying new pages..."
	cp -R $(API_DOCS_OUTPUT_DIR)/*  $(API_DOCS_WEB_TEMP)/
	@echo ">>> Commiting changes..."
	cd $(API_DOCS_WEB_TEMP) ; \
		rm -f index.html && cp doc_index.html index.html ; \
		git add -A . && git commit -a -m 'New version' && git push

00-docs-pdf-run: docs-api
	@echo ">>> Creating development docs (PDF)..."
	@PYTHONPATH=$(PACKAGE_DIR):$$PYTHONPATH \
	    CANDELABRA_PREFIX=$(TOP) \
	    CANDELABRA_CONF=$(TOP)/conf/candelabra.conf \
	    LD_LIBRARY_PATH=$(TOP)/lib:$$LD_LIBRARY_PATH   \
	    DYLD_LIBRARY_PATH=$(TOP)/lib:$$DYLD_LIBRARY_PATH   \
		    sphinx-build -q -b latex  \
		        $(API_DOCS_DIR)  $(API_DOCS_OUTPUT_DIR)/latex
	make -C  $(API_DOCS_OUTPUT_DIR)/latex   all-pdf
	@echo ">>> PDF documentation at $(API_DOCS_OUTPUT_DIR)/latex"
	@cp $(API_DOCS_OUTPUT_DIR)/latex/*.pdf   $(TOP)/  && echo ">>> PDFs also copied at $(TOP)"

docs-pdf:          clean-docs all 00-docs-pdf-run


####################################################################################################
# test & coverage

.PHONY: test test-fast 00-test-run
.PHONY: coverage coverage-fast

00-test-run:
	@echo ">>> Running unit tests FAST..."
	$(NOSE_SCRIPT) -w $(PACKAGE_TESTS_DIR)
	@echo ">>> done!"

test:               $(MAIN_SCRIPT) 00-test-run
test-fast:                         00-test-run

00-coverage-run:
	@echo ">>> Creating coverage report for the node..."
	@[ -d $(COVERAGE_DOCS_OUTPUT_DIR) ] || mkdir $(COVERAGE_DOCS_OUTPUT_DIR)
	@rm -rf $(COVERAGE_DOCS_OUTPUT_DIR)/*
	$(NOSE_SCRIPT) --with-xcoverage \
	      --xcoverage-file=coverage.xml \
	      --cover-package=candelabra \
	      --cover-erase \
	      --cover-html \
	      --cover-html-dir=$(COVERAGE_DOCS_OUTPUT_DIR)
	@echo ">>> Documentation left at $(COVERAGE_DOCS_OUTPUT_DIR)"

coverage:              $(MAIN_SCRIPT)  00-coverage-run
coverage-fast:                         00-coverage-run


