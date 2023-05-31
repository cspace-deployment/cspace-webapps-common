test:
	echo 'starting tests `date`'
	bash ./deploy-ucb.sh -a -e pycharm
	cd ../working_dir
	coverage run manage.py test
	coverage report

clean:
	git clean -fd
	# git reset --hard
	git checkout main
	git pull -v

