import csv
import sys
import time
import traceback
import configparser


def getRecords(rawFile, key):
    try:
        f = open(rawFile, 'r', encoding='utf-8')
        csvfile = csv.reader(f, delimiter="|")
    except IOError:
        message = 'Expected to be able to read %s, but it was not found or unreadable' % rawFile
        return message, -1
    except:
        raise

    try:
        columns = 0
        records = []
        for row, values in enumerate(csvfile):
            records.append(values)
            if len(values) > columns:
                columns = len(values)
        return records, columns
    except IOError:
        message = 'Could not read (or maybe parse) rows from %s' % rawFile
        return message, -1
    except:
        raise


if __name__ == "__main__":

    if len(sys.argv) == 5:
        print("MEDIA: input file 1 (fully qualified path): %s" % sys.argv[1])
        print("MEDIA: input file 2 (fully qualified path): %s" % sys.argv[2])
    else:
        print()
        print("usage: %s <findcommandresult> <cspacemedia> <cspaceaccessions> <outputfile>" % sys.argv[0])
        print("e.g.   %s findcommandresult.txt cspacemedia.csv cspaceaccessions.csv outputfile.csv" % sys.argv[0])
        print()
        sys.exit(1)

    stats = {}
    records1, columns1 = getRecords(sys.argv[1], 1)
    if columns1 == -1:
        print('MEDIA: Error! %s' % sys.argv[1])
        sys.exit()
    print('MEDIA: %s columns and %s lines found in file %s' % (columns1, len(records1), sys.argv[1]))
    stats[f'input: {sys.argv[1]}'] = len(records1)

    records2, columns2 = getRecords(sys.argv[2], 1)
    if columns2 == -1:
        print('MEDIA: Error! %s' % sys.argv[2])
        sys.exit()
    errors = 0
    media_info = {}
    for r in records2:
        if len(r) == 13:
            media_info[r[1]] = r
        else:
            print(r)
            errors += 1
    print('MEDIA: %s columns and %s lines found in file %s' % (columns2, len(records2), sys.argv[2]))
    stats[f'input: {sys.argv[2]}'] = len(records2)

    records3, columns3 = getRecords(sys.argv[3], 1)
    if columns3 == -1:
        print('MEDIA: Error! %s' % sys.argv[3])
        sys.exit()
    errors = 0
    accession_info = {}
    for r in records3:
        if len(r) == 2:
            accession_info[r[1]] = r
        else:
            print(r)
            errors += 1
    print('MEDIA: %s columns and %s lines found in file %s' % (columns3, len(records3), sys.argv[3]))
    stats[f'input: {sys.argv[3]}'] = len(records3)

    outputfh = csv.writer(open(sys.argv[4], 'w'), delimiter="|")
    # the first row of the file is a header
    columns = records2[0]
    del records2[0]
    outputfh.writerow(['filepath', 'image found', 'accession found'] + columns)

    filenames = {}
    for i, r in enumerate(records1):
        f  = r[0]
        fn = f.split('/')[-1]
        if '.JPG' in f or '.CR2' in f:
            fn = fn.replace('.JPG','').replace('.CR2','')
            fn = fn.split('_')[0]
            filenames[fn] = f
    stats[f'filenames'] = len(filenames)

    stats['image found in cspace'] = 0
    stats['image not in cspace'] = 0
    stats['accession exists'] = 0
    stats['accession not found'] = 0
    for f in filenames:
        if f in accession_info:
            accession_exists = 'accession exists'
        else:
            accession_exists = 'accession not found'
        stats[accession_exists] += 1
        if f in media_info:
            outputfh.writerow([filenames[f]] + ['image found', accession_exists] + media_info[f])
            stats['image found in cspace'] += 1
        else:
            outputfh.writerow([filenames[f]] + ['image not in cspace', accession_exists])
            stats['image not in cspace'] += 1

    for s in sorted(stats):
        print(f'{s} {stats[s]}')
