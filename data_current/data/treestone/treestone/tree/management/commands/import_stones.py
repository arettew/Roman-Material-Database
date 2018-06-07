
"""
This is a sample script to import data from a CSV into Django. It assumes you
will be running this on a Python3 instance of Django ~= 1.11. It also requires
customization and will not work on its own, since it is dependent on the
specific Django models and fields you have created. It is explicitly not set
up to be run multiple times on the same items (as it will create duplicates
and can clash with uniqueness constraints).
To enable the command, in a Django application (one below the project level),
create folders like the following:
mkdir -p myproj/myapp/management/commands/
This will create a series of directories that Django uses to situate the import
command in its own manage.py framework. At the bottom most directory create a
file called 'import_modelname.py', where the 'modelname'
is the model you are importing.
 and paste the contents of this gist, i.e
myproj/myapp/management/commands/import_modelname.py
The assumption is that you will have one model to one CSV, but this can be
adapted for generating multiple models from one CSV file also. You will need
to import the model in the appropriate place below and handle it in the action
portion of your script. This is also true for models associated by foreign key
which will likely require some code snippets from the CDH dev team. However,
am example of how this might work is also included.
You can then use the project's manage.py to run the script:
python manage.py import_modelname path/to/mydata.csv
"""

# These imports are Python modules that are used to carry out the import
import csv

from django.core.management.base import BaseCommand

# EDIT ME: with an import of myapp.models and model name
# where your model name goes, camel-cased precisely as it is in myapp/models.py
# so if your app was plinyletters and the model was Letter,
# the import would be: from plinyletters.models import Letter
from treestone.tree.models import Stones, Bibliography, CitationStone

# EDIT ME: Foreign Key relationship from MyModel example
# If you are not dealing with a Foreign Key relationship in the model, then
# delete any imports on the line below these comemnts.
# Foreign Key imports will need to be listed in their associated CSV row
# i.e., A person will need their address listed in their row, but you'll
# use the address fields to create an Address object in Django.


def map_csv(csvfile, headers=True):
    """
    This function does the actual work of importing the CSV and mapping it to a
    model.
    You will need to customize this to make it do anything useful.
    You should map header names from your CSV to fields on your model.
    Foreign key associations need to be created manually via Django's
    ORM syntax. When you're ready to add that portion, speak to a member of the
    CDH dev team, but we've given you an example to get you started using an
    association of Person with a single Address.
    """
    # Create an empty model instance of your model above
    # EDIT ME: Use your model's name
    

    reader = csv.DictReader(csvfile)

    for row in reader:
        # - EDIT ME
        # where 'last_name' and 'first_name' are column headings in your CSV
        stone = Stones()
        print(row)
        stone.name = row['name']
        stone.alternate_name = row['alternate_name']
        stone.petrographic_details = row['petrographic_details']
        stone.age = row['age']
        stone.appearance = row['appearance']
        stone.poisson_ratio = row['poisson_ratio']
        stone.absorption = row['absorption']
        stone.quarry_location = row['quarry_location']
        stone.archaeological_sources = row['archaeological_sources']
        stone.primary_sources = row['primary_sources']
        stone.secondary_sources = row['secondary_sources']
        stone.shapefile = row['shapefile']
        stone.notes = row['notes']
        stone.dates_of_use = row['dates_of_use']
        stone.density_avg = row['density_avg']
        stone.density_low = row['density_low']
        stone.density_high = row['density_high']
        stone.elastic_modulus_average = row['elastic_modulus_average']
        stone.elastic_modulus_low = row['elastic_modulus_low']
        stone.elastic_modulus_high = row['elastic_modulus_high']
        stone.image = row['image']
        stone.rupture_modulus_average = row['rupture_modulus_average']
        stone.rupture_modulus_low = row['rupture_modulus_low']
        stone.rupture_modulus_high = row['rupture_modulus_high']
        stone.compressive_strength_average = row['compressive_strength_average']
        stone.compressive_strength_low = row['compressive_strength_low']
        stone.compressive_strength_high = row['compressive_strength_high']

        stone.save()

        cite_names = []
        # iterate through the items and if they
        # end with _cite append them.
        for k, v in row.items():
            if k.endswith('_cite'):
                cite_names.append(k)

        for cite_name in cite_names:
            # if the row has an actual value and isn't empty
            if row[cite_name]:
                # split the citation numbers
                cite_numbers = row[cite_name].split(';')
                # for each number in the numbers
                # grab the bibliograpy and create a CitationTree obj.
                for number in cite_numbers:
                    if number.strip():
                        biblio = Bibliography.objects.get(bib_no=number)
                        # split by _ , omit _cite and rejoin
                        orig_name = '_'.join(cite_name.split('_')[:-1])
                        CitationStone.objects.create(
                            bibliography=biblio,
                            stone=stone,
                            stone_attribute=orig_name
                            )
       


class Command(BaseCommand):

    def add_arguments(self, parser):
        # we add one argument, the path to the CSV to import
        # this should need no customization
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        """
        Handle is the default function called by the Command, and will always
        be executed.
        You will need to custom one setting for your CSV, depending on whether
        or not it has headers.
        """

        # open the file using a with statement, so that the program
        # closes the file cleanly. This is standard python practice.
        with open(options['path'], 'r', errors='replace') as csvfile:
            map_csv(csvfile)
