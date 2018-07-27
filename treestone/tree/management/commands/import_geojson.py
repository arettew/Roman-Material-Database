from django.core.management.base import BaseCommand
from treestone.tree.models import Trees, Stones 

import os, re

# Reads the geojson files that correspond to a specific materialType ("trees"/"stones")
def readFiles(materialType): 
    path = "treestone/tree/static/geojson/" + materialType + "/"
    for fileName in os.listdir(path):
        geojsonFile = open(path + fileName, "r")

        name = re.sub(path, "", geojsonFile.name)
        name = name[:name.index(".")]
        name = re.sub("_", " ", name)
        loadGeojsonToObject(geojsonFile, name, materialType)

# Loads geojson to an object depending on the materialType ("trees"/"stones")
def loadGeojsonToObject(geojsonFile, name, materialType):
    # Look for file name 
    try:
        if materialType == "trees":
            materialQuery = Trees.objects.filter(common_name__icontains=name)
        else: 
            materialQuery = Stones.objects.filter(name__icontains=name)
    except: 
        print("Error with " + materialType + ": " + name)
        return
    
    count = materialQuery.count()
    if (count == 0):
        print("Error with " + materialType + ": No items found for " + name)
        return 
    elif (count > 1):
        print("Error with " + materialType + ": Too many items found for " + name)
        return 

    material = materialQuery[0]
    geojson = geojsonFile.read()
    material.geojson = geojson
    material.save()
    

    

class Command(BaseCommand):

    def handle(self, *args, **options):
        readFiles("trees")
        readFiles("stones")
        