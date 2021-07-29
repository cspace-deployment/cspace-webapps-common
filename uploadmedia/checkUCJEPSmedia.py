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

    if len(sys.argv) == 4:
        print("MEDIA: input file 1 (fully qualified path): %s" % sys.argv[1])
        print("MEDIA: input file 2 (fully qualified path): %s" % sys.argv[2])
    else:
        print()
        print("usage: %s <findcommandresult> <cspacemedia> <outputfile>" % sys.argv[0])
        print("e.g.   %s findcommandresult.csv cspacemedia.cfg outputfile.cfg" % sys.argv[0])
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

    outputfh = csv.writer(open(sys.argv[3], 'w'), delimiter="|")
    # the first row of the file is a header
    columns = records2[0]
    del records2[0]
    outputfh.writerow(['filepath'] + columns)

    filenames = {}
    for i, r in enumerate(records1):
        f  = r[0]
        fn = f.split('/')[-1]
        if '.JPG' in f or '.CR2' in f:
            fn = fn.replace('.JPG','').replace('.CR2','')
            filenames[fn] = f
    stats[f'filenames'] = len(filenames)

    stats['found in cspace'] = 0
    stats['not in cspace'] = 0
    for f in filenames:
        if f in media_info:
            outputfh.writerow([filenames[f]] + ['found'] + media_info[f])
            stats['found in cspace'] += 1
        else:
            outputfh.writerow([filenames[f]] + ['not in cspace'])
            stats['not in cspace'] += 1

    for s in sorted(stats):
        print(f'{s} {stats[s]}')
