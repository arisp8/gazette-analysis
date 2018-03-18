import sqlite3
import os
import errno
import sys
import platform
import zipfile
import stat

sys.path.insert(0, os.path.join(os.path.join(
    os.path.abspath(__file__).replace(__file__, '')), 'mmu'))

from mmu.utility.helper import Helper


# Sets up required elements for the application
def setup():
    if len(sys.argv) > 1:

        arg1 = sys.argv[1]

        # if --clean_install is specified then the previous sqlite
        # database is deleted.
        if arg1 == '--clean_install':
            print("Deleting SQLite Database")
            delete_sqlite_database()

        print("Setting up local database from scratch")
        setup_local_db()

    download_latest_chromedriver_release()
    # @todo: Test that everything has been set up correctly.


def delete_sqlite_database():
    try:
        os.remove('data/default')
        print("SQLite database has been deleted")
    except FileNotFoundError as e:
        print("File has not been found")
    except PermissionError as e:
        print("File could not be deleted")


# Takes care of setting up the local SQLite database
def setup_local_db():

    # Creates the data folder if not exists
    try:
        os.makedirs('mmu/data')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    db = sqlite3.connect('mmu/data/default')
    cursor = db.cursor()

    # Executes the default.sql to create default database schema
    install_sql = open('install/default.sql', 'r', encoding='utf8').read()
    cursor.executescript(install_sql)

    db.commit()
    cursor.close()
    db.close()


def download_latest_chromedriver_release():

    if os.path.isfile('drivers/chromedriver'):
        print('chromedriver is already downloaded')
        return

    endpoint = 'https://chromedriver.storage.googleapis.com/'
    + '{version}/{file_name}'

    latest_release_link = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'
    latest_version = Helper.get_url_contents(latest_release_link).strip()

    if platform.system() == 'Linux':
        file = 'chromedriver_linux64.zip'
    elif platform.system() == 'Darwin':
        file = 'chromedriver_mac64.zip'
    elif platform.system() == 'Windows':
        file = 'chromedriver_win32.zip'
    else:
        print('Chromedriver is not supported on your OS.')
        return

    download_page = endpoint.format(version=latest_version, file_name=file)

    # Creates the data folder if not exists
    try:
        os.makedirs('drivers')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    if Helper.download(download_page, 'chromedriver.zip', 'drivers'):
        print('chromedriver.zip downloaded successfully')
        zip_ref = zipfile.ZipFile('drivers/chromedriver.zip', 'r')
        zip_ref.extractall('drivers')
        zip_ref.close()
        print('chromedriver extracted successfully from chromedriver.zip.')
        os.remove('drivers/chromedriver.zip')
        print('chromedriver.zip removed successfully')
        
        if platform.system() == 'Windows':
            os.chmod('drivers/chromedriver.exe', 0o755)
        else:
            os.chmod('drivers/chromedriver', 0o755)
    else:
        print('Downloading chromedriver for selenium failed.')


if __name__ == '__main__':
    setup()
