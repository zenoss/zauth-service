#============================================================================
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
_COMPONENT            = $(strip $(COMPONENT))
SUPERVISOR_CONF       = $(_COMPONENT)_supervisor.conf
SUPERVISORD_DIR       = $(pkgconfdir)/supervisor

#============================================================================
# Hide common build macros, idioms, and default rules in a separate file.
#============================================================================
#---------------------------------------------------------------------------#
# Pull in zenmagic.mk
#---------------------------------------------------------------------------#
# Locate and include common build idioms tucked away in 'zenmagic.mk'
# This holds convenience macros and default target implementations.
#
# Generate a list of directories starting here and going up the tree where we
# should look for an instance of zenmagic.mk to include.
#
#     ./zenmagic.mk ../zenmagic.mk ../../zenmagic.mk ../../../zenmagic.mk
#---------------------------------------------------------------------------#
NEAREST_ZENMAGIC_MK := $(word 1,$(wildcard ./zenmagic.mk $(shell for slash in $$(echo $(abspath .) | sed -e "s|.*\(/obj/\)\(.*\)|\1\2|g" | sed -e "s|[^/]||g" -e "s|/|/ |g"); do string=$${string}../;echo $${string}zenmagic.mk; done | xargs echo)))

ifeq "$(NEAREST_ZENMAGIC_MK)" ""
    $(warning "Missing zenmagic.mk needed by the $(COMPONENT)-component makefile.")
    $(warning "Unable to find our file of build idioms in the current or parent directories.")
    $(error   "A fully populated src tree usually resolves that.")
else
    include $(NEAREST_ZENMAGIC_MK)
endif

# Specify install-related directories to create as part of the install target.
INSTALL_MKDIRS = $(_DESTDIR)$(_prefix) $(_DESTDIR)$(prefix)/log $(_DESTDIR)$(SUPERVISORD_DIR) $(_DESTDIR)$(pkgconfdir)/$(_COMPONENT) $(_DESTDIR)$(prefix)/var/$(_COMPONENT)

#============================================================================
# Subset of standard build targets our makefiles should implement.  
#
# See: http://www.gnu.org/prep/standards/html_node/Standard-Targets.html#Standard-Targets
#============================================================================
.PHONY: all clean devinstall distclean install installhere help mrclean uninstall uninstallhere
all:

$(INSTALL_MKDIRS):
	$(call cmd,MKDIR,$@)

install installhere: | $(INSTALL_MKDIRS) 
	$(warning "Installing zauth conf files.")
	$(call cmd,CP,,conf/*,$(_DESTDIR)$(pkgconfdir)/$(_COMPONENT)/)
	$(call cmd,SYMLINK, ../$(_COMPONENT)/$(SUPERVISOR_CONF),$(_DESTDIR)$(SUPERVISORD_DIR)/$(SUPERVISOR_CONF))
	@$(call echol,$(LINE))
	@$(call echol,"$(_COMPONENT) installed to $(_DESTDIR)$(prefix)")

devinstall: dev% : %
	@$(call echol,"Add logic to the $@ rule if you want it to behave differently than the $< rule.")

uninstall: dflt_component_uninstall
	$(call cmd,RMDIR,$(_DESTDIR)$(pkgconfdir)/$(_COMPONENT))
	$(call cmd,RMDIR,$(_DESTDIR)$(SUPERVISORD_DIR)/$(SUPERVISOR_CONF))

uninstallhere:
	$(call cmd,RMDIR,$(_DESTDIR))

mrclean distclean: dflt_component_distclean

help: dflt_component_help
