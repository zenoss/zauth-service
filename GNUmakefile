
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
#============================================================================
.DEFAULT_GOAL   := help # all|build|clean|distclean|devinstall|install|help

#============================================================================
# Build component configuration.
#
# Beware of trailing spaces.
# Don't let your editor turn tabs into spaces or vice versa.
#============================================================================
COMPONENT             = zauth
COMPONENT_PREFIX      = install
COMPONENT_SYSCONFDIR  = $(COMPONENT_PREFIX)/etc
_COMPONENT            = $(strip $(COMPONENT))
SUPERVISOR_CONF       = $(_COMPONENT)_supervisor.conf
SUPERVISORD_DIR       = $(SYSCONFDIR)/supervisor
REQUIRES_JDK          = 0
REQUIRES_PYTHON       = 0
SRC_DIR               = src
BUILD_DIR             = build
DIST_DIR              = dist
PIP                   ?= $(shell which pip)
PYTHON                ?= $(shell which python)

PIPINSTALL = $(PIP) install -i http://zenpip.zendev.org/simple

#============================================================================
# Hide common build macros, idioms, and default rules in a separate file.
#============================================================================
ifeq "$(wildcard zenmagic.mk)" ""
    $(error "Makefile for $(_COMPONENT) is unable to include zenmagic.mk.  Please investigate")
else
    include zenmagic.mk
endif

# List of source files needed to build this component.
COMPONENT_SRC ?= $(DFLT_COMPONENT_SRC)

COMPONENT_TAR ?= $(DFLT_COMPONENT_TAR)

COMPONENT_NAME ?= $(DFLT_COMPONENT_NAME)

# Specify install-related directories to create as part of the install target.
# NB: Intentional usage of _PREFIX and PREFIX here to avoid circular dependency.
INSTALL_MKDIRS = $(_DESTDIR)$(_PREFIX) $(_DESTDIR)$(PREFIX)/log $(_DESTDIR)$(PREFIX)/etc/supervisor $(_DESTDIR)$(PREFIX)/etc/$(_COMPONENT) $(_DESTDIR)$(PREFIX)/var/$(_COMPONENT)

#============================================================================
# Subset of standard build targets our makefiles should implement.  
#
# See: http://www.gnu.org/prep/standards/html_node/Standard-Targets.html#Standard-Targets
#============================================================================
.PHONY: all build clean devinstall distclean install help mrclean uninstall
all build: $(TARGET_TAR)

$(INSTALL_MKDIRS):
	$(call cmd,MKDIR,$@)

install: | $(INSTALL_MKDIRS) 
	$(warning "Installing zauth conf files.")
	$(call cmd,CP,,conf/*,$(_DESTDIR)$(PREFIX)/etc/$(_COMPONENT)/)
	$(call cmd,SYMLINK, ../$(_COMPONENT)/$(SUPERVISOR_CONF),$(_DESTDIR)$(PREFIX)/etc/supervisor/$(SUPERVISOR_CONF))
	@$(call echol,$(LINE))
	@$(call echol,"$(_COMPONENT) installed to $(_DESTDIR)$(PREFIX)")

devinstall: dev% : %
	@$(call echol,"Add logic to the $@ rule if you want it to behave differently than the $< rule.")

uninstall: dflt_component_uninstall
	$(call cmd,RM,-rf,$(_DESTDIR)$(PREFIX)/etc/$(_COMPONENT))
	$(call cmd,RM,-rf,$(_DESTDIR)$(SUPERVISORD_DIR)/$(SUPERVISOR_CONF))

clean: dflt_component_clean
	-$(call cmd,PYTHON,setup.py,clean)
	$(call cmd,RM,-rf,$(BUILD_DIR))
	$(call cmd,RM,-rf,$(DIST_DIR))

mrclean distclean: dflt_component_distclean

help: dflt_component_help
