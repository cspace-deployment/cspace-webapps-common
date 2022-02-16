import csv
import os
import sys


def pluralize(n, w):
    if n == 1:
        return '%s %s' % (n, w)
    else:
        return '%s %ss' % (n, w)


def checkJobs(jobs, joberrors, report_type):
    totals = {}

    print("Bulk Media Uploader Progress Report\n")
    print("job directory: %s" % DIR)

    columnheaders = 'step1 original processed inprogress discrepancy error messages seen'.split(' ')
    # print("\t".join(columnheaders))
    for c in columnheaders: totals[c] = 0

    output_lines = []
    ingested = []
    for i, job in enumerate(sorted(jobs.keys(), reverse=True)):

        steps = jobs[job]

        try:
            steps['discrepancy'] = steps['original'] - steps['processed']
        except:
            try:
                steps['discrepancy'] = steps['original']
            except:
                steps['discrepancy'] = -1
        # if steps['discrepancy'] == 0: del steps['discrepancy']
        if job in joberrors:
            steps['error messages seen'] = joberrors[job]
        else:
            steps['error messages seen'] = 0

        output_line = job + ":\t"

        if steps['discrepancy'] == 0:
            output_line += '%s ingested' % pluralize(steps['original'], 'media file')
        else:
            try:
                output_line += '%s uploaded, %s ingested, %s' % (
                    pluralize(steps['original'], 'media file'), pluralize(steps['processed'], 'media file'),
                    pluralize(steps['discrepancy'], 'problem'))
            except:
                if 'check' in steps:
                    output_line += 'job failed qc check; %s attempted' % pluralize(steps['check'], 'media file')
                elif 'step1' in steps:
                    output_line += 'job pending, %s' % pluralize(steps['step1'], 'media file')
                else:
                    output_line += 'run files incomplete %s' % steps
        if steps['error messages seen'] != 0:
            output_line += '%s error messages seen in trace.log' % (steps['error messages seen'])
        for step in columnheaders:
            if step in steps:
                totals[step] += steps[step]

        try:
            ingested.append((job, steps['processed']))
        except:
            # print(f'no processed media found for {job}')
            pass

        if i >= 20 and report_type == 'summary':
            pass
        else:
            output_lines.append(output_line)

    if report_type == 'summary': print('most recent %s jobs:\n' % len(output_lines))
    print('\n'.join(output_lines))

    statsfile = f'/var/cspace/monitor/{sys.argv[4]}.bmu.stats.csv'
    fh = open(statsfile, 'w')
    stats = csv.writer(fh, delimiter="\t")
    [stats.writerow(r) for r in ingested]

    print("\ntotal number of jobs found: %s " % len(jobs.keys()))
    print("\ngrand totals:\n")
    for step in columnheaders:
        if totals[step] != 0:
            print('%s %s ' % (step, totals[step]))
    print()


def checkMissing(images, missing):
    for name in images:
        isMissing = True
        runs = images[name]
        for run in runs:
            steps = runs[run]
            for step in steps:
                if step in 'processed|step1|inprogress'.split('|'): isMissing = False

    if isMissing: print(name, '::: \tmissingname\n')


def checkDuplicates(images, duplicates):
    for name in sorted(duplicates):
        if duplicates[name] > 1: print('%s duplicated %s times' % (name, duplicates[name]))
    print()


def checkCsids(csids):
    for name in sorted(csids):
        print(name + "\t",)
        CSIDlist = csids[name]
        print(CSIDlist['objectnumber'] + '\t',)
        for type in 'blob media object'.split(' '):
            print(','.join(CSIDlist[type]),'\t',)
        print()


def checkSteps(images):
    for name in sorted(images):
        print(name + "\t",)
        runs = images[name]
        for run in runs:
            print(run + "\t",)
            steps = runs[run]
            for step in steps:
                print(step + "\t",)
        print()


def usage():
    print("usage: python checkRuns.py <bmu_directory> <jobs missing duplicates images csids> <full summary>")


########## Main ##############
if len(sys.argv) < 4:
    usage()
    sys.exit(1)

DIR = sys.argv[1]
images = {}
jobs = {}
missing = {}
duplicates = {}
joberrors = {}
errors = {}
csids = {}
JOB = {}

if (sys.argv[1]):  # if we have a single job, just do stats for it..
    JOB = sys.argv[1]

if (sys.argv[3] in ['full', 'summary']):
    report_type = sys.argv[3]
else:
    print('report type must be either "full" or "summary".')
    sys.exit(1)

files = []

for filename in os.listdir(DIR):
    if not '.csv' in filename: continue
    try:
        (run, step, extension) = filename.split('.')
    except:
        # skip .csv files that don't match the pattern
        continue
    FH = open(os.path.join(DIR, filename), 'r')
    delimx = '\t'
    for i, line in enumerate(FH.readlines()):
        line = line.strip()
        objectCSID = ''
        mediaCSID = ''
        blobCSID = 'not provided'
        description = 'not provided'
        objectnumber = ''
        if i == 0:
            if '|' in line: delimx = '|'
            header = line.split(delimx)
            continue
            # print('x\t' + sys.argv[4] + '\t' + step + '\t' + str(len(header)) + '\t' + line.replace('|','\t'))
        else:
            cells = line.split(delimx)
        try:
            for i, h in enumerate(header):
                if h == 'objectCSID':
                    objectCSID = cells[i]
                elif h == 'mediaCSID':
                    mediaCSID = cells[i]
                elif h == 'blobCSID':
                    blobCSID = cells[i]
                elif h == 'name':
                    name = cells[i]
                elif h == 'objectnumber':
                    objectnumber = cells[i]
        except:
            print('problem with file %s' % filename)
            break
        if objectCSID == 'not found': continue
        if not run in jobs: jobs[run] = {}
        if not step in jobs[run]: jobs[run][step] = 0
        if not name in images: images[name] = {}
        if not run in images[name]: images[name][run] = {}
        if not step in images[name][run]: images[name][run][step] = 0
        jobs[run][step] += 1
        images[name][run][step] += 1
        if step == 'processed':
            if not name in duplicates: duplicates[name] = 0
            duplicates[name] += 1
        if 'original' in step or 'step1' in step: missing[name] = filename
        if not name in csids:
            csids[name] = {'media': [], 'object': [], 'blob': []}
        csids[name]['objectnumber'] = objectnumber
        if step == 'processed':
            if mediaCSID and not mediaCSID in csids[name]['media']: csids[name]['media'].append(mediaCSID)
            if objectCSID and not objectCSID in csids[name]['object']: csids[name]['object'].append(objectCSID)
            if blobCSID and not blobCSID in csids[name]['blob']: csids[name]['blob'].append(blobCSID)

for filename in os.listdir(DIR):
    if not '.trace.log' in filename: continue
    FH = open(os.path.join(DIR, filename), 'r')
    filename = filename.replace('.trace.log', '')
    joberrors[filename] = 0
    for i, line in enumerate(FH.readlines()):

        error = False
        # next if /\/tmp\/upload_cache\/name/ # special case
        if 'Missing file' in line: error = True
        if 'Post did not return a 201 status code' in line: error = True
        if 'No output file' in line: error = True
        if error:
            # print(_."\n")
            name = line.split(' ')
            joberrors[filename] += 1
            # print("error filename :: name :: error\n")
            errors[name] += error

if (sys.argv[2] == 'jobs'):
    checkJobs(jobs, joberrors, report_type)

elif (sys.argv[2] == 'missing'):
    checkMissing(images, missing)

elif (sys.argv[2] == 'duplicates'):
    checkDuplicates(images, duplicates)

elif (sys.argv[2] == 'images'):
    checkSteps(images)

elif (sys.argv[2] == 'csids'):
    checkCsids(csids)

else:
    usage()
