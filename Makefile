all: clean compile

change-version:
	bin/change-version.sh $(version)

compile:
	bin/compile.sh $(version)

package:
	bin/package.sh

deploy:
	bin/deploy.sh

test:
	bin/test.sh

clean:
	bin/clean.sh
