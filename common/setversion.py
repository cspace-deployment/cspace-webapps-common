from os import popen


def getversion():
    try:
        version = popen("/usr/bin/git describe --always").read().strip()
        if version == '':  # try alternate location for git (this is the usual Mac location)
            version = popen("/usr/local/bin/git describe --always").read().strip()
        version_file = open('VERSION', 'w')
        version_file.write(version + '\n')
    except:
        try:
            version = open('VERSION', 'r').read().strip()
            version_file.close()
        except:
            version = 'Unknown'
    return version


print(getversion(), 'set as this version in VERSION')
