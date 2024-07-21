import sqlite3
import os
import shutil
import datetime
import time
import re
from datetime import datetime, timedelta

conn = sqlite3.connect('/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db')
cur = conn.cursor()

#Path



adve_destination = "/home/pi/ADATA/MultiMedia/Undelete/Movies/Adventures/"

#Rating
rshits = 30 #rate less than 5.5
rlow = 90 #Rate less than 6.5
rnormal = 150 #Rate less than 7.5
rhight = 200 #Rate less than 8.5

def rmdir():

#Remove Files by Rating and dates

    def rmfiles(rate_from, rate_to, days):
        print(f'{rate_from} - {rate_to}')
        
        today = datetime.datetime.now()
        
        for (root, dirs, files) in os.walk(source, topdown=False):
            for f in files:
                #Search all files from source
                file_path = os.path.join(root, f)
                #print(f'File name: {f}')
                #look for file modified
                timestamp_of_file_modified = os.path.getmtime(file_path)
                #print(f'modifation time: {timestamp_of_file_modified}')
                #
                modification_date = datetime.datetime.fromtimestamp(timestamp_of_file_modified)
                #print(f'Modifation date: {modification_date}')
                #
                number_of_days = (datetime.datetime.now() - modification_date).days
                #
                #print(f'Days: {number_of_days}')
                rate = re.findall("Rate ([^)]*)" ,f)
                rate = sum(map(float, rate))
                #print(f'Rate: {rate}')
                
                if rate > rate_from and rate < rate_to and days < number_of_days:
                    
                    os.remove(file_path)
                    print(f'File Removed: {f}')


def moveMoviesByCountryFiles(Country):
    conn.commit()
    query = """SELECT file, path 
    FROM metadata_items as md 
    INNER JOIN library_sections as ls ON ls.id = md.library_section_id 
    INNER JOIN media_items as mi ON mi.metadata_item_id = md.id 
    INNER JOIN media_parts as mp ON mp.media_item_id = mi.id 
    INNER JOIN directories as dir ON mp.directory_id = dir.id 
    INNER JOIN media_streams as ms ON ms.media_item_id = mi.id 
    WHERE ls.name in ('Films') 
    AND md.tags_country LIKE ? 
    AND file NOT LIKE ?"""

    cur.execute(query, (Country, '%Undelete%'))

    print("Files Movied")
    destination = "/home/pi/ADATA/MultiMedia/Undelete/Movies/",Country,"/"
    rows = cur.fetchall()
    
    for row in rows:
        filePath = os.path.join(row[0])
        folderName = os.path.join(row[1])
        filename = filePath.split("/")[-1]
        undeleteSubdir = os.path.join(destination+folderName)
        os.makedirs(undeleteSubdir, exist_ok=True)
        if os.path.isfile(undeleteSubdir+"/"+filename):
            print('The file exist')
            os.remove(filePath)
            print('The file removed from main folder')
        else:
            shutil.move(filePath, undeleteSubdir)
            print(filename, " Movied to", undeleteSubdir)

def moveMoviesByGenreFiles(Genre):
    conn.commit()
    query = """SELECT file, path 
    FROM metadata_items as md 
    INNER JOIN library_sections as ls ON ls.id = md.library_section_id 
    INNER JOIN media_items as mi ON mi.metadata_item_id = md.id 
    INNER JOIN media_parts as mp ON mp.media_item_id = mi.id 
    INNER JOIN directories as dir ON mp.directory_id = dir.id 
    INNER JOIN media_streams as ms ON ms.media_item_id = mi.id 
    WHERE ls.name in ('Films') 
    AND ms.codec in ('eac3', 'aac', 'ac3','ac4', 'mp3', 'dca', 'ass') 
    AND md.tags_genre LIKE ? 
    AND file NOT LIKE ?"""

    cur.execute(query, (Genre, '%Undelete%'))

    print("Files Movied")
    destination = "/home/pi/ADATA/MultiMedia/Undelete/Movies/",Genre,"/"
    rows = cur.fetchall()
    
    for row in rows:
        filePath = os.path.join(row[0])
        folderName = os.path.join(row[1])
        filename = filePath.split("/")[-1]
        undeleteSubdir = os.path.join(destination+folderName)
        os.makedirs(undeleteSubdir, exist_ok=True)
        if os.path.isfile(undeleteSubdir+"/"+filename):
            print('The file exist')
            os.remove(filePath)
            print('The file removed from main folder')
        else:
            
            shutil.move(filePath, undeleteSubdir)
            print(filename, " Movied to", undeleteSubdir)


def printFilesWithRating(rateFrom , rateTo, section, removeDates):
    conn.commit()
    
    query = dbFilter()
    cur.execute(query, (rateFrom, rateTo, section, '%Undelete%'))
    rows = cur.fetchall()
    for row in rows:
        filepath = row[0]
        directory = row[1]
        rating = row[2]
        #updateTime = row[3]
        if get_modification_date(filepath)>removeDates:
            try:
                #removeFileInDays(filepath, removeDates)
                get_modification_date(filepath)
                print('The ',directory, ' with rating ',rating, 'modify date ',get_modification_date(filepath), ' removed after ', removeDates)   
            except:
                continue

def removeFileInDays(filepath, days):
    if os.path.isfile(filepath):
        if get_modification_date(filepath) > days:
            os.remove(filepath)

def get_modification_date(filepath):
    # Get the last modified time of the file
    file_mtime = os.path.getmtime(filepath)
    # Convert the time in seconds since epoch to a datetime object
    modification_date = datetime.datetime.fromtimestamp(file_mtime)
    current_date = datetime.datetime.now()
    delta = current_date - modification_date
    return delta.days

def moveFiles(vasileiosPiTvRecordsFilePath, destinationTvRecordsFilePath):
    for (root, dirs, files) in os.walk(vasileiosPiTvRecordsFilePath, topdown=False):
            for f in files:
                #Search all files from source
                filePath = os.path.join(root, f)
                folders = filePath.split("/")
                subFolder = folders[len(folders)-2]
                if os.path.isfile(destinationTvRecordsFilePath+subFolder):
                    print('The file exist')
                    os.remove(destinationTvRecordsFilePath+subFolder+"/"+f)
                    print('The file removed from main folder: '+destinationTvRecordsFilePath+subFolder+"/"+f)
                else:
                    current_time = datetime.now()
                    file_mod_time = datetime.fromtimestamp(os.path.getmtime(vasileiosPiTvRecordsFilePath))
                    time_diff = current_time - file_mod_time
                    if(time_diff <= timedelta(hours=6)):
                        print("Start move File :"+ f)
                        shutil.move(filePath, destinationTvRecordsFilePath+subFolder)
                        print(f, " Movied to", destinationTvRecordsFilePath+subFolder)
                    

def curentDateMinusEpochTime(epochTime):
    # Get the current date and time
    current_datetime = datetime.now()
    # Calculate the difference between the current date and the epoch date
    difference = current_datetime - epochTime

    # Convert the difference to days
    days_since_epoch = difference.days

    print(f"Number of days since the Unix epoch: {days_since_epoch}")

def dbFilter():
    query = """SELECT file, path, audience_rating, mi.updated_at 
    FROM metadata_items as md 
    INNER JOIN library_sections as ls ON ls.id = md.library_section_id 
    INNER JOIN media_items as mi ON mi.metadata_item_id = md.id 
    INNER JOIN media_parts as mp ON mp.media_item_id = mi.id 
    INNER JOIN directories as dir ON mp.directory_id = dir.id 
    WHERE audience_rating BETWEEN ? AND ? AND name = ? AND file NOT LIKE ?
    """
    return query

#moveMoviesByCountryFiles('%Czech%')
#moveMoviesByCountryFiles('%Greek%')
#moveMoviesByGenreFiles('%Animovaný%')
moveFiles("/home/pi/VasileiosPi/usb/" , "/home/pi/ADATA/MultiMedia/Weekly/Serials/")
printFilesWithRating(0,2,'Films', 15)
printFilesWithRating(2,3,'Films', 30)
printFilesWithRating(3,4,'Films', 45)
printFilesWithRating(5,5.5,'Films', 60)
printFilesWithRating(5.5,6,'Films', 90)
printFilesWithRating(6,6.5,'Films', 120)
printFilesWithRating(6.5,7,'Films', 150)
printFilesWithRating(7,7.5,'Films', 180)
printFilesWithRating(7.5,8,'Films', 210)
printFilesWithRating(8,8.5,'Films', 240)



conn.close()