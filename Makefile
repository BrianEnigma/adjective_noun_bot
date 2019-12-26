HERE=$(shell pwd)
all: deploy

deploy: package
	cd package; zip -r ../adjective_noun_bot.zip *
	#cd package; zip -r ../adjective_noun_bot.zip * .libs_cffi_backend
	#aws s3 cp lambda_ebooks.zip s3://blah/blah/blah

package: mastodon adjectivenounbot.py local_settings-mastodon.py
	mkdir -p package
	cp -R mastodon/* ./package/
	#cp -R mastodon/.libs_cffi_backend ./package/
	cp adjective.txt ./package/
	cp noun.txt ./package/
	cp adjectivenounbot.py ./package/
	cp local_settings-mastodon.py local_settings.py
	cp local_settings.py ./package/

mastodon:
	rm -rf mastodon
	mkdir -p mastodon
	echo '[install]' > ./mastodon/setup.cfg
	echo 'prefix=' >> ./mastodon/setup.cfg
	cd $(HERE)/mastodon ; pip3 install mastodon.py -t $(HERE)/mastodon
	
clean:
	rm -rf package

distclean: clean
	rm -rf mastodon

