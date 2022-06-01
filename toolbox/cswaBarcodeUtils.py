import codecs, csv, datetime, os, re, subprocess, sys

def send_to_s3(dataType, printerDir, filepath, bare_filename):
    script_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.stderr.write(os.path.join(script_path, 'toolbox', 'cp_only_s3.sh') + f'{filepath} barcode/{dataType}/{printerDir}/{bare_filename}')
    p_object = subprocess.Popen(
        [os.path.join(script_path, 'toolbox', 'cp_only_s3.sh'), f'{filepath}', f'barcode/{dataType}/{printerDir}/{bare_filename}'])
    pid = ''
    if p_object._child_created:
        pid = p_object.pid
        return f'sent barcode file to printer as: {dataType}/{printerDir}/{bare_filename}'
    else:
        raise

def uploadCmdrWatch(location, printerDir, dataType, filenameinfo, data, config):
    try:
        barcode_dir = '/cspace/batch_barcode'

        # slugify the location
        slug = re.sub('[^\w-]+', '_', location).strip().lower()
        bare_filename = f'{slug}_{datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")}_{filenameinfo}.txt'

        #localslug = re.sub('[^\w-]+', '_', barcodeFile).strip().lower()
        barcode_path = '%s/%s' % (barcode_dir, bare_filename)
        barcodeFh = codecs.open(barcode_path, 'w', 'utf-8-sig')
        csvlogfh = csv.writer(barcodeFh, delimiter=",", quoting=csv.QUOTE_ALL)
        if dataType == 'locationLabels':
            csvlogfh.writerow('termdisplayname'.split(','))
            for d in data:
                csvlogfh.writerow((d[0],))  # writerow needs a tuple or array
        elif dataType == 'objectLabels':
            csvlogfh.writerow(
                'MuseumNumber,ObjectName,PieceCount,FieldCollectionPlace,AssociatedCulture,EthnographicFileCode'.split(','))
            for d in data:
                csvlogfh.writerow(d[3:9])
        barcodeFh.close()
        send_to_s3(dataType, printerDir, barcode_path, bare_filename)
    except:
        return '<span style="color:red;">could not write to %s</span>' % barcode_path

    try:
        return f'barcode/{dataType}/{printerDir}/{bare_filename}'
    except:
        os.unlink(barcode_path)
        return '<span style="color:red;">could not transmit %s to S3. Check parameters and connection</span>' % f'barcode/{dataType}/{printerDir}/{bare_filename}'
    