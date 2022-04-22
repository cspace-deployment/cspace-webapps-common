rm -rf ${HOME}/services
git clone https://github.com/cspace-deployment/services.git
cd ${HOME}/services
git checkout origin/bampfa_5.1
cp services/report/3rdparty/jasper-cs-report/src/main/resources/*.jrxml ~/jrxml
git checkout origin/botgarden_5.1
cp services/report/3rdparty/jasper-cs-report/src/main/resources/*.jrxml ~/jrxml
git checkout origin/cinefiles_5.1
cp services/report/3rdparty/jasper-cs-report/src/main/resources/*.jrxml ~/jrxml
git checkout origin/pahma_5.1
cp services/report/3rdparty/jasper-cs-report/src/main/resources/*.jrxml ~/jrxml
git checkout origin/ucjeps_5.1
cp services/report/3rdparty/jasper-cs-report/src/main/resources/*.jrxml ~/jrxml
cd
rm -rf ${HOME}/services
