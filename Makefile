URL=http://lab.hakim.se/reveal-js
REPO=https://github.com/hakimel/reveal.js/archive/master.zip
THEME=gfdl
FLAGS=-s \
	  -f rst -t revealjs \
	  --slide-level=2 \
	  -V revealjs-url=./reveal.js \
	  -V theme=${THEME} \
	  -V slideNumber=true \
	  --template=gfdl.revealjs \
	  --no-highlight \
	  --mathjax

D2FILES=$(wildcard d2/*.d2)
D2FIGURES=$(patsubst %.d2,%.svg,$(subst d2/,img/,$(D2FILES)))

SOURCE=$(wildcard src/*.F90)

all: index.html reveal.js $(DOTFIGURES) $(D2FIGURES)

reveal.js:
	wget -N ${REPO}
	unzip master.zip
	mv reveal.js-master reveal.js

reveal.js/css/theme/gfdl.css: gfdl.css
	mkdir -p reveal.js/css/theme
	cp gfdl.css reveal.js/css/theme/

index.html : slides.txt gfdl.revealjs reveal.js/css/theme/gfdl.css $(DOTFIGURES) $(SOURCE)
	pandoc ${FLAGS} $< -o $@
	sed -i 's/^" data-start-line=/"><code data-start-line=/g' $@
	#sed -i 's/^"><code>/">/g' $@
	sed -i 's/<li class="fragment"/<li/g' $@
	sed -i 's/<video /<video autoplay loop /g' $@

img/%.svg: d2/%.d2
	d2 $^ $@ --pad 2

img/fixedprec.svg: dot/fixedprec.dot
	dot -Tsvg:cairo $^ > $@

clean:
	rm -f index.html
	#rm -f $(DOTFIGURES)
