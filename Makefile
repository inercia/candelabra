
TOP=.

# the system python we will use for bootstrapping
SYS_PYTHON=python2.7

# Buildout
BUILDOUT=$(TOP)/bin/buildout
BUILDOUT_ARGS=-t 120

# the boostrap file
BOOTSTRAP_PY_URL=http://svn.zope.org/*checkout*/zc.buildout/trunk/bootstrap/bootstrap.py
BOOTSTRAP_FILE=$(TOP)/buildout/bootstrap.py
BOOTSTRAP_ARGS=--version=2.2.1 --config-file=$(BUILDOUT_CONF)

# directories we need for running the server but are not automatically created
RUN_DIRS=\
         logs \
         run  \
         var  var/lib

# cleanup some things after building...
POST_BUILD_CLEANUPS=\
        doc  man *~

# RPM creation
RPM_TAR=$(TOP)/pkg.tar
RPM_FILES=README.rst
RPM_DIRS=\
         $(RUN_DIRS) \
         bin conf include lib sbin share \
         html  html/static \
         share/doc \
         scripts
RPM_BUILD_ROOT=/tmp/candelabra-buildroot

# where the sources are and how to build them
PACKAGE_DIR=$(TOP)/candelabra
PACKAGE_TESTS_DIR=$(TOP)/tests
SETUP_PY=$(TOP)/setup.py

# the main script
MAIN_SCRIPT=$(TOP)/bin/candelabra
NOSE_SCRIPT=nosetests-2.7

# API docs dir
API_GEN=sphinx-apidoc
API_DOCS_DIR=$(TOP)/docs/api/
API_DOCS_OUTPUT_DIR=$(TOP)/docs/api/build

COVERAGE_DOCS_OUTPUT_DIR=$(TOP)/docs/coverage

# nose arguments
NOSE_ARGS=--with-xunit  --all-modules

BUILDOUT_CONF=$(TOP)/buildout.cfg

####################################################################################################

all: devel

$(BUILDOUT): $(BOOTSTRAP_FILE)
	@echo ">>> Bootstraping..."
	@[ -d downloads ] || mkdir downloads
	$(SYS_PYTHON) $(BOOTSTRAP_FILE) $(BOOTSTRAP_ARGS)
	@echo ">>> Bootstrapping SUCCESSFUL!"

00-common:
	@echo ">>> Running buildout for DEVELOPMENT..."
	PATH=$(TOP)/bin:$$PATH $(BUILDOUT) -N $(BUILDOUT_ARGS) -c $(BUILDOUT_CONF)
	@echo ">>> Checking dirs..."
	@for i in $(RUN_DIRS) ; do mkdir -p $$i ; done
	@rm -rf $(POST_BUILD_CLEANUPS)
	@echo

$(MAIN_SCRIPT): $(BUILDOUT) 00-common

devel: $(BUILDOUT)
	@echo ">>> Running buildout for DEVELOPMENT..."
	PATH=$(TOP)/bin:$$PATH $(BUILDOUT) -N $(BUILDOUT_ARGS) -c $(BUILDOUT_CONF)
	@echo ">>> Build SUCCESSFUL !!"
	@echo ">>> You can now 'make docs', 'make coverage'..."

fast: $(BUILDOUT)
	@echo ">>> Running FAST buildout. I hope we have all dependencies installed..."
	PATH=$(TOP)/bin:$$PATH $(BUILDOUT) -N $(BUILDOUT_ARGS) -o  -c $(BUILDOUT_CONF)
	@rm -rf $(POST_BUILD_CLEANUPS) $(TOP)/pip-*
	@echo ">>> Fast-build SUCCESSFUL !!"
	@echo ">>> You can now 'make docs', 'make coverage'..."


####################################################################################################
# cleanup



clean-pyc: 
	@echo ">>> Cleaning pyc..."
	rm -f     `find $(PACKAGE_DIR) $(PACKAGE_TESTS_DIR) -name '*.pyc'`
	rm -f     `find $(PACKAGE_DIR) $(PACKAGE_TESTS_DIR) -name '*.pyo'`

clean-dcache:
	rm -rf    $(TOP)/downloads

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

run-cleanup:
	@echo ">>> Cleaning up things..."
	@[ -d logs ] || mkdir logs
	@[ -d logs ] && rm -rf logs/*
	@[ -d run ] || mkdir run
	@[ -d run ] && rm -rf run/*
	@echo ">>> Checking dirs..."
	@for i in $(RUN_DIRS) ; do mkdir -p $$i ; done

####################################################################################################
# distribution

sdist:
	$(SYS_PYTHON) setup.py sdist

bdist:
	$(SYS_PYTHON) setup.py bdist

####################################################################################################
# run

run: run-cleanup
	@echo ">>> Running the Candelabra..."
	@PYTHONPATH=$(PACKAGE_DIR):$$PYTHONPATH \
		LD_LIBRARY_PATH=$(TOP)/lib:$$LD_LIBRARY_PATH       \
		DYLD_LIBRARY_PATH=$(TOP)/lib:$$DYLD_LIBRARY_PATH   \
		$(MAIN_SCRIPT) --config=$(TOP)/conf/candelabra.conf

####################################################################################################
# documentation

# note: on Mac OS X, set "LC_ALL=en_US.UTF-8" and "LANG=en_US.UTF-8" for docs generation

clean-docs:
	@echo ">>> Cleaning docs..."
	rm -rf    $(API_DOCS_OUTPUT_DIR)

docs-api:
	@echo ">>> Creating API docs..."
	rm -f $(API_DOCS_DIR)/candelabra.*.rst
	ABS_PACKAGE_DIR=`pwd`/$(PACKAGE_DIR) ; \
	    $(API_GEN) --force -o $(API_DOCS_DIR) -d 8 -s rst  $$ABS_PACKAGE_DIR  \
	    `find $$ABS_PACKAGE_DIR -name tests`

.PHONY: 00-docs-run
00-docs-run: docs-api
	@echo ">>> Creating development docs..."
	@PYTHONPATH=$(PACKAGE_DIR):$$PYTHONPATH \
	    CANDELABRA_PREFIX=$(TOP) \
	    CANDELABRA_CONF=$(TOP)/conf/candelabra.conf \
	    LD_LIBRARY_PATH=$(TOP)/lib:$$LD_LIBRARY_PATH   \
	    DYLD_LIBRARY_PATH=$(TOP)/lib:$$DYLD_LIBRARY_PATH   \
		    sphinx-build -q -b html  $(API_DOCS_DIR)  $(API_DOCS_OUTPUT_DIR)
	@echo ">>> Documentation left at $(API_DOCS_OUTPUT_DIR)/doc_index.html"

.PHONY: docs
docs:              clean-docs all 00-docs-run

.PHONY: 00-docs-pdf-run
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


.PHONY: docs-pdf
docs-pdf:          clean-docs all 00-docs-pdf-run


####################################################################################################
# test & coverage

.PHONY: 00-test-run
00-test-run:
	@echo ">>> Running unit tests FAST..."
	$(NOSE_SCRIPT) -w $(PACKAGE_TESTS_DIR)
	@echo ">>> done!"

.PHONY: test
test:               $(MAIN_SCRIPT) 00-test-run
.PHONY: test-fast
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

.PHONY: coverage
coverage:              $(MAIN_SCRIPT)  00-coverage-run
.PHONY: coverage-fast
coverage-fast:                         00-coverage-run


00-pylint-run:
	@echo ">>> Creating pylint report..."
	@PYTHONPATH=$(PACKAGE_DIR):$$PYTHONPATH \
	$(TOP)/bin/pylint --rcfile=$(TOP)/buildout/pylintrc $(PACKAGE_DIR)
	@echo ">>> done!"

.PHONY: pylint
pylint:              $(MAIN_SCRIPT)  00-pylint-run
.PHONY: pylint-fast
pylint-fast:                         00-pylint-run



