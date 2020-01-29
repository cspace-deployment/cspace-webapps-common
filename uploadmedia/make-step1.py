import os, sys

header = 'name|size|objectnumber|date|creator|contributor|rightsholder|imagenumber|handling|approvedforweb|description'
template = 'f{name}|f{size}|f{doc_id}||||||f{handling}|on|f{description}'

description = 'automatically generated pdf'
handling = ''
size = ''

rootDir = sys.argv[1]
for dirName, subdirList, fileList in os.walk(rootDir):
    print('directory: %s' % dirName)
    job_file = open(f'/tmp/bmu/{dirName}.step1.csv', 'w')
    job_file.write(header)
    for name in fileList:
        doc_id = name.replace('.pdf', '')
        job_file.write(template)
        print('\t%s' % name)
    job_file.close()