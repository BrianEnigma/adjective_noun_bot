HERE=$(shell pwd)
all: deploy

deploy: package
	cd package; zip -r ../adjective_noun_bot.zip *
	#aws s3 cp lambda_ebooks.zip s3://blah/blah/blah

package: python-twitter mastodon adjectivenounbot.py local_settings.py
	mkdir -p package
	cp -R mastodon/* ./package/
	cp -R python-twitter/* ./package/
	cp adjective.txt ./package/
	cp noun.txt ./package/
	cp adjectivenounbot.py ./package/
	cp local_settings.py ./package/

python-twitter:
	rm -rf python-twitter
	mkdir -p python-twitter
	echo '[install]' > ./python-twitter/setup.cfg
	echo 'prefix=' >> ./python-twitter/setup.cfg
	cd $(HERE)/python-twitter ; pip3 install python-twitter -t $(HERE)/python-twitter

mastodon:
	rm -rf mastodon
	mkdir -p mastodon
	echo '[install]' > ./mastodon/setup.cfg
	echo 'prefix=' >> ./mastodon/setup.cfg
	cd $(HERE)/mastodon ; pip3 install mastodon.py -t $(HERE)/mastodon

clean:
	rm -rf package

distclean: clean
	rm -rf python-twitter mastodon

