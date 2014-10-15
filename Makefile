WATCH_FILE = .watch-pid
MANAGE_SCRIPT = ./bin/manage.py
SITE_DIR = ./_site
STATIC_DIR = ./varify/static
JAVASCRIPT_DIR = ${STATIC_DIR}/js
JAVASCRIPT_SRC_DIR = ${JAVASCRIPT_DIR}/src
JAVASCRIPT_MIN_DIR = ${JAVASCRIPT_DIR}/min

SASS_DIR = ${STATIC_DIR}/stylesheets/scss
CSS_DIR = ${STATIC_DIR}/stylesheets/css

COMPILE_SASS = `which sass` \
	--scss \
	--style=compressed \
	-r ${SASS_DIR}/lib/bourbon/lib/bourbon.rb \
	${SASS_DIR}:${CSS_DIR}

REQUIRE_OPTIMIZE = `which node` ./bin/r.js -o ${JAVASCRIPT_DIR}/app.build.js

all: setup build collect

build: sass optimize

setup:
	@if [ ! -f ./varify/conf/local_settings.py ] && [ -f ./varify/conf/local_settings.py.sample ]; then \
	    echo 'Creating local_settings.py...'; \
	    cp ./varify/conf/local_settings.py.sample ./varify/conf/local_settings.py; \
	fi;

collect:
	@echo 'Symlinking static files...'
	@${MANAGE_SCRIPT} collectstatic --link --noinput > /dev/null

sass: _ensure
	@echo 'Compiling Sass/SCSS...'
	@${COMPILE_SASS} --update

watch: _ensure unwatch
	@echo 'Watching in the background...'
	@${COMPILE_SASS} --watch > /dev/null 2>&1 & echo $$! >> ${WATCH_FILE}

unwatch:
	@if [ -f ${WATCH_FILE} ]; then \
		echo 'Watchers stopped'; \
		for pid in `cat ${WATCH_FILE}`; do kill -9 $$pid; done; \
		rm ${WATCH_FILE}; \
	fi;

optimize: _ensure clean
	@echo 'Optimizing JavaScript...'
	@${REQUIRE_OPTIMIZE} > /dev/null

clean:
	@rm -rf ${JAVASCRIPT_MIN_DIR}

_ensure:
	@mkdir -p ${JAVASCRIPT_SRC_DIR} ${JAVASCRIPT_MIN_DIR} ${SASS_DIR} ${CSS_DIR}


.PHONY: all build sass watch unwatch optimize
