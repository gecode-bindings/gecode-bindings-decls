GECODEDIR := $(shell g++ $(CPPFLAGS) $(CXXFLAGS) -H -E gecodedir.hh 2>&1 >/dev/null | grep gecode/kernel.hh | awk '{print $$2}' | sed 's|/kernel.hh||')
GECODECONFIG := $(GECODEDIR)/support/config.hpp
GECODEVERSION := $(shell cat $(GECODECONFIG) | egrep '\<GECODE_VERSION\>' | awk '{print $$3}' | sed 's/"//g')
PROTOTYPES = data/gecode-prototypes-$(GECODEVERSION).yml
ENUMS = data/gecode-enums-$(GECODEVERSION).yml

all: prelude main

prelude:
	test -e $(ENUMS) || rm -f $(PROTOTYPES)

main: $(PROTOTYPES)

$(PROTOTYPES): xml/namespaceGecode.xml extractor.py
	python3 extractor.py $(GECODEVERSION)

xml/namespaceGecode.xml: Doxyfile
	doxygen Doxyfile

Doxyfile: Doxyfile.in
	cat $< | sed "s#@GECODEDIR@#$(GECODEDIR)#" > $@ || { rm -f $@; exit 1; }

clean:
	-rm -rf *~ Doxyfile xml

.PHONY: all prelude main clean
