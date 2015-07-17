TR= $(wildcard i18n/*.ts)
CTR= $(TR:.ts=.qm)
TRAD_DIR= i18n

all: resources_rc.py $(CTR)

resources_rc.py: resources.qrc
	pyrcc4 -o $@ $^

$(TRAD_DIR)/%.qm: $(TRAD_DIR)/%.ts
	lrelease $^

clean:
	rm resources_rc.py $(TRAD_DIR)/*.qm