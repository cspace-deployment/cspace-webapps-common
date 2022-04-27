rm -rf ${HOME}/services
git clone https://github.com/cspace-deployment/services.git
cd ${HOME}/services
git checkout origin/ucb_6.0
# copy 'core' reports
cp services/report/3rdparty/jasper-cs-report/src/main/resources/*.jrxml ~/jrxml
# copy reports for all tenants
cp services/report/3rdparty/jasper-cs-report/src/main/resources/tenants/*/*.jrxml ~/jrxml
cd
rm -rf ${HOME}/services
