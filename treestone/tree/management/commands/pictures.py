from django.core.management.base import BaseCommand
from treestone.tree.models import Trees, Stones 
import os 
from string import ascii_lowercase
import csv

# Maps a given trait of an object to the object's row in the csv
def mapRowToTrait(csvFile, column):
    reader = csv.DictReader(csvFile)

    items = {}
    # Count starts at two since row is headers
    count = 2
    for row in reader: 
        items[row[column]] = count
        count = count + 1
    
    return items 

# Renames the pictures 
def renamePictures(itemsToRows, materialType):
    for name in itemsToRows.keys(): 
        try:
            if materialType == "stones": 
                material = Stones.objects.get(name=name)
            else:
                material = Trees.objects.get(common_name=name)
        except: 
            continue

        oldPath = "treestone/tree/static/images/" + materialType
        newPath = "treestone/tree/static/images/" + materialType + "_new"
        # Try renaming first picture, if it exists
        oldName = oldPath + "/AT" + str(itemsToRows[name]) + ".jpg"
        newName = newPath + "/AT" + str(material.pk) + ".jpg"
        try:
            os.rename(oldName, newName)
        except: 
            print("Error converting " + str(itemsToRows[name]))

        # Try renaming subsequent pictures, if they exist
        # Exclude 'a'
        letters = ascii_lowercase[1:]
        for letter in letters: 
            oldName = oldPath + "/AT" + str(itemsToRows[name]) + letter + ".jpg"
            newName = newPath + "/AT" + str(material.pk) + letter + ".jpg"
            try:
                os.rename(oldName, newName)
            except: 
                break

# This is meant to be a one-time command. Uncomment the code in handle to use 
class Command(BaseCommand):
    # Renames pictures so that their number matches the pk of the object in the database
    def handle(self, *args, **options):
        #treeCsvFile = open("treestone/tree/static/csvs/trees.csv", "r")
        #itemsToRows = mapRowToTrait(treeCsvFile, 'common_name')
        #renamePictures(itemsToRows, "trees")

        stoneCsvFile = open("treestone/tree/static/csvs/pietra.csv", "r")
        itemsToRows = mapRowToTrait(stoneCsvFile, "name")
        renamePictures(itemsToRows, "stones")