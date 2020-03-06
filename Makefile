test:
	echo 'starting tests `date`'
	bash ./setup.sh configure pycharm
	bash ./setup.sh deploy pahma
	coverage run manage.py test
	coverage report

clean:
	git clean -fd
	# git reset --hard
	git checkout master
	git pull -v

