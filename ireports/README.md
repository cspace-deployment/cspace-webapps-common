
for the webapps (iReports) to work properly
in the home directory of the user under which this webapp is running there needs to be
a directory called jrxml that has all the .jrxml files for all deployments.

the script getjrxml.sh does the following:

- clones the service repo
- checks out the 5.1 branch for each tenant
- copies the .jrxml files for each tenant into ~/jrxml
- gets rid of the clone

