## cspace-webapps-common

[![build status](https://travis-ci.com/cspace-deployment/cspace-webapps-common.svg?branch=master)](https://travis-ci.com/cspace-deployment/cspace-webapps-common)

This Django project supports easy access to various CollectionSpace services. To preview
several deployments of this project at UC Berkeley, visit: https://webapps.cspace.berkeley.edu.

The following components are provided with this project:

#### Core Applications (user-facing apps that you might actually use)

* grouper - helps manage group membership of collectionobjects
* imagebrowser - a "lightbox-like" app that tiles images based on a keyword query to Solr backend
* imageserver - cacheing proxy server to serve images from CSpace server
* imaginator - "google-lookalike" search app -- provides "N blue links" for a keyword search
* ireports - interface to installed reports that take inputs other than CSIDs
* internal - internal (authenticating) search appliance
* search - public (non-authenticating) search appliance
* permalinks - a permanent link for an object; renders a single object nicely
* uploadmedia - "bulk media uploader" (BMU)

#### Helper Applications (needed by other apps, e.g. search)

* suggest - provides term suggestions (GET request, returns JSON)
* suggestpostgres - provides term suggestions from database via Postgres queries
* suggestsolr - provides term suggestions from Solr core via Solr facet queries
* landing - a "landing page" to ease navigation between apps
* mobileesp - mobile device support; only slightly used so far

#### "Demo" Applications (only to show how this 'framework' works, and to show how to access CSpace)

* hello - simple default app to help you figure out if your Django deployment is working
* service - proxies calls to services; mostly for test purposes

#### Directories (which you'll need to understand, and/or put stuff in)

* config - put your config files here. This directory is git-ignored
* cspace_django_site - "core" site code -- urls.py, settings.py, etc.
* fixtures - fixtures are used by several apps to provision nav bar and other items
* authn - need by authentication backend. Basically: do not touch
* common - code used across all apps

#### More Obsure Applications (disabled by default, but available)

* simplesearch - make query (kw=) to collectionobjects service, display list_items
* batchuploadimages -- RESTful interface to upload images in bulk (_EXPERIMENTAL!_)

### Quick Start Guide

The following dialog makes a number of assumptions -- that your system is already more-or-less setup for Python and Postgres development; that your existing codebase is recent enough (see version requirements below), etc.

```bash
# get the code. This is the bleeding edge development repo.
git clone https://github.com/cspace-deployment/cspace-webapps-common
cd cspace-webapps-common
# resolve the Python module requirements.
# you'll need to have the PostgreSQL client code as well as the Python setuptools installed...
# on a Mac *most* of this is in XCode Tools... consider 'sudo pip' if you know what you are doing
# other code managers such as homebrew can help with this too.
pip install -r pycharm_requirements.txt
# configure Django for your environment. 'pycharm' is the least demanding.
# note that you'll need npm and node installed on your system.
./setup.sh configure pycharm
# deploy a tenant. 'default' points to 'nightly.collectionspace.org'. otherwise, roll your own.
./setup.sh deploy default
# if it all works...
python manage.py runserver
# if the server comes up OK, you should see a landing page in your browser at
http://localhost:8000
# if so, your webapps are pretty much working!
```

### Less Quick Guide: Setting Up for Development or Production

##### Caveats and General Observations

* As illustrated in the Quick Start Guide, the process to deploy this Django project is pretty conventional: get code, resolve system dependencies, configure, and start 'er up. At the moment, the project does not use any of the popular deployment systems out there, e.g. Kubernetes or Docker. Instead, you have to do it "by hand", but there are helpers!

* For starters, you'll need to set up Django and install some Python modules (see the various `*_requirements.txt` files)

* The project does run in a variety of different environments: we've got it working with RedHat (RHEL6, Ubuntu, and MacOS). There are some version sensitivities, mostly but probably not completely captured in the various `*_requirements.txt` files.

* Next you'll need to `configure` your project for a particular target environment: `prod`, `dev`, or `pycharm`.  The first two options are of course intended to support running the webapps in either of two server environments.  As a developer, you'll probably want to use the `pycharm` target, which is only a little different from the other two: it does not deploy the image caching option, and it turns off Universal Analytics.

* You need to have a CollectionSpace server to point to. Even before you start playing with your own, you should consider deploying the *Sample Deployment*, which points to the development server at `nightly.collectionspace.org`.  This setup is quite easy to get working -- few dependencies, and all the assumptions about configuration are made for you.

* So -- `configuration` is used here to talk about the setup required for different environments, and `deployment` is used to refer setting up the project for the particular CollectSpace tenant (server) you will be using. Got it?

* A helper script called `setup.sh` is provided to help with all this. It is described in some detail below. You should use it -- there are lots of details in the setup process! Strictly speaking, thought, it is not required -- you can putter around with the files yourself if you know what you're doing. `setup.sh` remembers to perform all the little Django details required when setting up and maintaining the project, but note there may be times when you'll need to go around it, at least in development.

* This project comes with **sample** configuration files that point to the development server at `nightly.collectionspace.org`. These are located in `config.examples/`, and you can deploy them by typing './setup.sh deploy default' on the command line when in the `cspace-webapps-common` directory. NB: the files in `config/` are 'git-ignored'. For your deployment, you'll need to modify these files for your deployment: to point to your real CollectSpace server, your logo, etc. And you'll need to keep track of your versions. We suggest making your own GitHub or other repo for your files; if you model the structure of the UCB configuration repo (e.g. https://github.com/cspace-deployment/cspace-webapps-ucb), you'll be able to use the `deploy` option in `setup.sh` to manage deployment of your own webapps.

* So. To summarize. Almost all webapps require a config file, some require two. Therefore, the `config` will be quite full of config files for the varioius apps. An example configuration file for each webapp is included, but you *will* eventually need to make your own. If the webapp is called `webapp`, the corresponding configuration file should be called `webapp.cfg` unless there is a good reason not to.

##### Recipe for Development Deployments

The following recipe assumes you are deploying in a development environment, on a Mac, RedHat, or Ubuntu system. And that you will use the development server that comes with Django or that you'll be using PyCharm as your IDE (it has a builtin server). If you are deploying in a UCB-managed server environment (i.e. Red Hat), see further below.

First, fork the `cspace-deployment/cspace-webapps-common` in your own account on GitHub.

Then on your development system, you'll want to clone your development fork of the repo in whatever directory you do your PyCharm development in. For me, I put them all in `~/PyCharmProjects`.

You'll need to install a number of Python modules (see `*_requirements.txt`).  PyCharm can help you with this, or you can
do something like the following:

Note: Before running `pip install -r pycharm_requirements.txt`, make sure that you have PostgreSQL, as well as the Python setuptools package installed, otherwise there will be errors.

```bash
# clone your fork of the github repo to wherever you want to deploy the webapps
# by default, the two repos go in your home directory; if you change the
# location, you'll need to edit setup.sh to indicate this.
cd ~
git clone https://github.com/<mygithubid>/cspace-webapps-common.git my_test_project
cd my_test_project/
# resolve the Python requirements
pip install -r pycharm_requirements.txt
```

NB: if you intend to use your "native python" you may need to resolve the requirements at the root level, e.g.

```bash
sudo pip install -r pycharm_requirements.txt
```

NB: Yes, you can, and indeed may have to, run your apps in a virtual environment if you are unable or unwilling to use the system defaults. This is covered below.  Also note that PyCharm can help you resolve module dependencies -- `venv` comes pretty much builtin
with PyCharm and supports multiple Python interpreters.

(At the moment, there are few version constraints for this project: Python 3.6+ and Django 2.2.9+; requirements.txt
specifies Django 2.2.9 or higher.)

You are now ready to configure your environment and deploy your tenant-specific parameters.

##### Using setup.sh

There is no `make` or `mvn` build/deploy process for Django webapps, and the deployment process consists of placing the code where it can be executed and customizing the parameters used for your particular case, which means editing configuration files by hand, or using ones provided for you (if you are working with an existing CSpace deployment, e.g. at UCB).

Instead there is a shell script called `setup.sh` which does the steps required to make your webapps go.

```
$ ./setup.sh
Usage: ./setup.sh <enable|disable|deploy|configure|show> <TENANT|CONFIGURATION|WEBAPP> [VERSION]

where: TENANT = 'default' or the name of a deployable tenant
       CONFIGURATION = <pycharm|dev|prod>
       WEBAPP = one of the available webapps, e.g. 'search' or 'ireports'
       VERSION = an option version number (i.e. GitHub tag)

e.g. ./setup.sh disable ireports
     ./setup.sh configure pycharm
     ./setup.sh deploy botgarden 5.1.0-rc-3
     ./setup.sh deploy pahma
     ./setup.sh show
```

```
# OPTION 1: sample deployment to see if you can get the project to run.
# configure your dev deployment
./setup.sh configure pycharm
# to setup the sample tenant configuration...
./setup.sh deploy default
# now you can start the development server
python manage.py runserver
# remember to ^C to stop the server
```

If you are working on one of the UCB tenants, you'll want to get the configuration files for that tenants. There are
example configurations for all UCB tenants in a separate GitHub repo. If you clone this repo in your home directory,
`setup.sh` will do the work of copying all the config files to the right place and initializing the Django project
to run them.

```
# OPTION 2: deploy one of the UCB configurations
# to deploy a specific tetant, you'll want to clone the repo with all the
# example config files out side of this repo, i.e. in ~/cspace-webapps-ucb
cd ; git clone https://github.com/cspace-deployment/cspace-webapps-ucb.git
cd ~/PycharmProjects/my_test_project
./setup.sh deploy ucjeps
# this will blow away whatever tenant might have been deployed previously in this repo and setup the UCJEPS tenant.
```

*NB: `setup.sh` expects this repo (`cspace-webapps-ucb`), with this exact name, to be in your home directory!*
*If your configuration directory is somewhere else or has a different name, edit the `CONFIGDIR` variable in `setup.sh` to point to yours.*

*NB: While most of the parameters for tenants are set up for Production, not all are. At any rate, you will need to make sure that the configuration files in `config` are indeed correct.*

As noted above you can disable any apps that you are not interested in. For example, if your collection does not have images
you will not be interested in any of the webapps named image\*. It is a simple matter to disable these, and you can
(re-)enable any time if you like. The process is illustrated below. If you don't, they will appear in the landing page
and you will need to configure them even if they won't really do anything.

```
# optional: disable any apps you don't want. the following apps only work if you have a solr datastore configured.
./setup.sh disable imageserver
./setup.sh disable imagebrowser
./setup.sh disable imaginator
```

To enable a disabled webapp do the following and restart the webserver you are using:

```
./setup.sh enable uploadmedia
```

To see which apps are enabled:

```
./setup.sh show
```

NB: this will show *all* apps, including the various helper apps, Django admin apps, etc.

(all the enable/disable functionality does is to comment out these webapps in `urls.py` and `installed_apps.py`; you *could* just do it yourself by hand.)


##### Deploying on RTL servers

*Caveat lector...these instructions are still quite raw, as is the deployment process itself. Suggestions welcome!*

A few important details, but do please read this whole section before you attempt to deploy on RTL servers:

* The actual recipe for a quick and painless deploment may be found [further below](#deploying-new-versions-on-rtl-servers). But do read on for the gory details.
* It is expected that a "release document" has been prepared in advance for any particular release, and a "deployment JIRA" exists as well. Please do check for these before attempting to deploy a new version!
* The Django webapps expected to deployed as user `app_webapps` using WSGI on RTL servers, and currently expects the deployed code to be in a tenant subdirectories in `/var/www`.  The application also *runs* under user `app_webapps`.
* The instructions below assume that you have followed the [initial instructions](#initial-setup-for-deployments-on-rtl-servers) (below) to set up the deployment scripts from the two repos.
* However, you should check to ensure that you have the latest versions of these scripts before deploying. Catch-22, sorry!
* Hope that's all clear!

###### Initial setup for deployments on RTL servers

If you haven't already done so, clone the two needed repo

```
ssh blacklight-prod.ets.berkeley.edu

sudo su - app_webapps

# only do this if it hasn't been done already...
# 1. easiest if to deploy repos in your home directory
cd
# 2. clone the two needed repos
git clone https://github.com/cspace-deployment/cspace-webapps-common
git clone https://github.com/cspace-deployment/cspace-webapps-ucb.git
```

There is a helper script for use in making Dev and Prod
deployments on RTL servers.

`deploy-ucb.sh` - deploys a particular version for specified museums

For initial setup, you'll need to:

* A Python virtual environment installed
* Requirements installed via pip (see above.)
* Apache configured appropriately (e.g. wsgi, passenger, etc.)

E.g.

```
(venv) app_webapps@blacklight-dev:~$ tail -1 .profile 
source /var/www/venv/bin/activate
```

Then you can deploy and start up the application.

###### Deploying new versions on RTL servers

On the RTL servers, you may assume that the two repos and scripts have
been set up in in the home directory of user `app_webapps` and are ready to use. In theory, only these two scripts are needed
to do a complete deployment.


First, stop Apache2 (see below).

To deploy and build the code from GitHub for pahma and cinefiles:
```
cd
cspace-webapps-common//deploy-ucb.sh -v 5.2.0-rc1 pahma cinefiles
```

or, to deploy them all, and keep a log of the deploy process:

```
cd
nohup time cspace-webapps-common/deploy-ucb.sh -a -v 5.3.0-rc14 > da-2020-02-07.txt &
```

... then start/restart Apache2 (see below).

NB:

* This script make assumptions about the RTL servers in use...!

Here's a recipe for actually deploying a new version on an RTL server:

1. Sign in to blacklight server (dev or prod)
1. Stop Apache
1. `sudo` to the app_webapps user
1. Deploy the new version
1. Exit the  shell
1. Start Apache
1. Verify in a browser that the application works

Here's a possible monologue:

```
ssh blacklight-dev.ets.berkeley.edu

sudo apache2ctl stop

sudo su - app_webappsp

# use the helper script to get and configure the new version for all tenants
./deploy-ucb.sh -v 5.2.0-rc1 -a
 
exit

sudo apache2ctl start

# check in browser that the app works...

exit
```

If you want to update just one deployment, you do NOT have to restart Apache.
Since we are running WSGI in "daemon mode", you can just touch the wsgi.py
file and WSGI will reload that one deployment:
```
cd
cspace-webapps-common//deploy-ucb.sh -v 5.2.0-rc1 pahma 
touch pahma/cspace_django_site/wsgi.py
```

_NB: authenticated webapp users for this deployment will need to 
log back in again after this!_

###### Rolling back on RTL servers

Right now, there is no way to rollback a release.

```
# to roll back...
```

##### Configuration files

Most webapps have an associated configuration file (with extension .cfg). The `search` apps also require a "field
definitions file" which describes all the fields used in search and display and this file is a carefully constructed
.csv file (tabs, no encapsulation).  All of these files need to be placed in the config/ directory and edited to point
to the target CSpace server. Lots of other defaults are set in these files as well. The files are in a (YAML-like) format that is consumed by the Python `ConfigParser` module.

E.g.

```YAML
[info]
logo              = https://nightly.collectionspace.org/collectionspace/ui/core/images/header-logo.png

[imaginator]
#
FIELDDEFINITIONS    = corepublicparms.csv
MAXRESULTS          = 100
TITLE               = Imaginator
```

You should make a version of each of the config files that you'll need, with values appropriate to your specific deployment and tenant.

The sample config files included with the project in `config.examples` point to `nightly.collectionspace.org`. These provide some limited functionality: `simplesearch` works, as does the single brain-damaged `iReport` that comes with CollectionSpace proper. The `service` webapp works, but note it has no config file: it accesses the server defined in the project's  authentication configuration in `main.cfg`.

### Starting and Stopping Development Servers

You have deployed the code from GitHub to the directory it will be executed in (or, you've cloned or forked this repo
on your local machine).

You have done the initial configuration with `setup.sh`.

You have `configured` your project and `deployed` your tenant-specific customizations.

Now you start a server...

##### Starting Django's built-in development server

From the command line, while in the project directory, type:

```
$ python manage.py runserver
```

and you should see:

```
Performing system checks...
System check identified 1 issue (0 silenced).
February 28, 2016 - 20:47:14
Django version 1.7, using settings 'cspace_django_site.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

##### Pycharm Debugger

In PyCharm, you'll need to do a bit of configuration before the project will run:

1. Enable Django Support

```
PyCharm > Preferences > Django
click: Enable Django Support
```

In the dialog window, ensure the following parameters show:

```
Django Project Root: /Users/jblowe/PyCharmProjects/cdp/cspace_django_site
Settings: settings.py
Manage script: /Users/jblowe/PyCharmProjects/cdp/cspace_django_site
```

2. Edit a "Run Configuraiton"

```
Run > Edit Configurations
```

In the dialog window,

```
Expand Defaults (by clicking on the little triangle)
Select: Django Server
Click + (to add a configuration)
Give your configuration a name, e.g. “cspace-webapps-common”
```

Environment variables:

```
DJANGO_SETTINGS_MODULE: cspace_django_site.settings
```

... and you will need to ensure that the Python interpreter being used is the right one -- the one that has all your requirements resolved.

Or you can resolve them in PyCharm, but you'll need to RTFM for that.

Now start the debugger! (click on the little ladybug in the upper right)

##### Your Project is Running!

Visit the base URL (locahost:8000 in both PyCharm and default dev server, who knows what in other environments!)

You will be rewarded with a landing page. Or more likely, you will have failed to meet all the setup conditions:

* The BMU and imageserver need to have directories created and accessible to work. If these are not there, the system will try to put files in `/tmp`.
* The needed config files better exist and have all the parms specified that are needed for the app.
* The additional module requirements (e.g. psycopg2 for Postgres) need to be met.
* The various directories for temp files and caches had better be there.