.DEFAULT_GOAL := help
HELP-DESCRIPTION-SPACING := 24

# ------- Help ----------------------- #
# Source: https://nedbatchelder.com/blog/201804/makefile_help_target.html
#
help:  ## Describe available tasks in Makefile
	@grep -h '^[a-zA-Z]' $(MAKEFILE_LIST) | \
	sort | \
	awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-$(HELP-DESCRIPTION-SPACING)s\033[0m %s\n", $$1, $$2}'
