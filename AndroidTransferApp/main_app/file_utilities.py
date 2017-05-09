import platform
import os


def print_prompt():
    f = open(os.path.dirname(os.path.realpath(__file__)) + '/prompt.txt', 'r')
    for line in f:
        print(line)
    print('\n')
    f.close()


def get_app_repo_location():
    return 'sdcard/Android/data/edu.rose_hulman.nswccrane.dataacquisition/files/records'


def get_slash():
    system_name = platform.system()
    if system_name == 'Linux':
        slash = '/'
    else:
        slash = '\\'
    return slash


def get_adb_ending():
    system_name = platform.system()
    if system_name == 'Linux':
        adb_ending = 'adb'
    else:
        adb_ending = 'adb.exe'
    return adb_ending


def get_adb_file_location():
    system_name = platform.system()
    base_location = os.path.dirname(os.path.realpath(__file__))
    if system_name == 'Linux':
        slash = '/'
        adb_file_location = base_location + slash + 'previous_adb_location.txt'
    else:
        slash = '\\'
        adb_file_location = base_location + slash + 'previous_adb_location.txt'

    return adb_file_location


def get_repo_file_location():
    system_name = platform.system()
    base_location = os.path.dirname(os.path.realpath(__file__))
    if system_name == 'Linux':
        slash = '/'
        repo_file_location = base_location + slash + 'previous_repo_location.txt'
    else:
        slash = '\\'
        repo_file_location = base_location + slash + 'previous_repo_location.txt'

    return repo_file_location


def read_from_adb_file():
    if not os.path.isfile(get_adb_file_location()):
        print('Must specify a new adb file location if no previous record of one exists. Not enough parameters')
        return None

    try:
        adb_file = open(get_adb_file_location(), 'r')
        adb_location = adb_file.readline()
        adb_file.close()
        if adb_location == '':
            print('No adb location on record')
            return None
        return adb_location
    except Exception as e:
        print('Could not read adb record file because of the following exception:')
        print(e)
        return None


def read_from_repo_file():
    if not os.path.isfile(get_repo_file_location()):
        print('Must specify a new destination for the transferred files if no record of one exists.',
              'Not enough parameters.')
        return None

    try:
        repo_file = open(get_repo_file_location(), 'r')
        repo_location = repo_file.readline()
        repo_file.close()
        if repo_location == '':
            print('No file repository location on record')
            return None
        return repo_location
    except Exception as e:
        print('Could not read transfer repository record file because of the following exception:')
        print(e)
        return None


def write_to_adb_file(new_adb_location):
    if not os.path.isdir(new_adb_location):
        print('New path to adb location is not a valid directory/path.',
              'Please retry with a valid path to the adb file')
        return None

    try:
        new_adb_location = new_adb_location + get_slash() + get_adb_ending()
        adb_file = open(get_adb_file_location(), 'w')
        adb_file.write(new_adb_location)
        adb_file.close()
        return new_adb_location
    except Exception as e:
        print('Could not read adb record file because of the following exception:')
        print(e)
        return None


def write_to_repo_file(new_repo_location):
    if not os.path.isdir(new_repo_location):
        print('New path to transfer file repository is not a valid directory/path.',
              'Please retry with a valid path to the directory you wish to transfer files to.')
        return None

    try:
        repo_file = open(get_repo_file_location(), 'w')
        repo_file.write(new_repo_location)
        repo_file.close()
        return new_repo_location
    except Exception as e:
        print('Could not read transfer repository record file because of the following exception:')
        print(e)
        return None
