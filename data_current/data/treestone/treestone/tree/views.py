from django.shortcuts import render

"""
You can use this to get a subset of your data out instead of using open refine or CTRL + Find

lives in your app
"""

import csv
import re

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.template import loader

#django generic class view 
from django.views.generic import ListView, DetailView 
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin

from django.forms.models import model_to_dict

#from treestone.tree.models import the model that you are using in model = MyModel
from treestone.tree.models import Stones
from treestone.tree.models import Trees
from treestone.tree.models import StoneImages 
from treestone.tree.models import TreeImages 
from treestone.tree.models import TreeEdits 
from treestone.tree.models import StoneEdits

#name this after whatever model you are mostly pulling from
class StonesListView(ListView):
    #change this based on what model you are interestsed in trees, stone, etc
    model = Stones

    def get_data(self):
      """
      Get data for MyModel as we see fit and pass it to a list of dictionaries
      for CSV Writer
      """
      # By default get_queryset() will get every instance of MyModel
      mymodels = self.get_queryset()
      # but we'll look at ways to filter it down later

      #making an array of dictionaries 
      dictionary_list = []
      for model in mymodels:
        model_dict = {}
        model_dict['name'] = model.name #if its just a simple attribute field
        model_dict['alternate_name'] = model.alternate_name
        # Here we're referencing a foreign key object and then its name
        #model_dict['bibliography'] = model_dict.bibliography.name
        # Here we're grabbing a Django managed m2m and th
        #model_dict['topics'] = [topic.name for topic
        #                        in ';'.join(model_dict.topics.all())
        # the syntax looks hairy but it isn't -- we're just telling python
        # to get all the related topics, and then make a list of their name
        # properties and join them with a semi-colon
        # psuedo code for getting through table data out
        #citations = StoneCitation.objects.filter(stone=stone)
        # model_dict['alternate_name_cite'] = citations.filter(column_name='alternate_name')[0].bibliography

        # now we append it to the list
        dictionary_list.append(model_dict)

      return dictionary_list
      #and that gets your data, you built the rows of your csv. 

    def render_to_response(self, context, **kwargs):

        # This boiler plate sets up the response and sets fields that tell
        # your browser this is a file, not a webpage.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="mymodel.csv"' #just change mymodel if you want to here

        # these need to match your dictionary above
        # if they don't python will complain
        headers = ['name', 'alternate_name']

        #you dont need to edit anything else in here  
        writer = csv.DictWriter(response, headers)
        writer.writeheader()
        rows = self.get_data()
        for row in rows:
            writer.writerow(row)

        return response 

"""
the query_set command is a way of getting what you want out of your models with a lot less pain, you can keep chaining them 

in the example on the git hub it had a model named topics, and it gets places in the topics object where the name is Foodbar. This will limit your models down to only those models for which that was true

The link djangos making queries: 
retreiving specific objects with filters
"""

class MapView(TemplateView):

    def get_context_data(self, **kwargs):
      context = super(MapView, self).get_context_data(**kwargs)
      return context

    def render_to_response(self, context, **kwargs):
      template_name = 'tree/map.html'
      template = loader.get_template(template_name)

      response = HttpResponse(template.render(context))
      return response

# Returns the GeoJSON for database entires, with featureType differentiating between trees 
# and stones 
@csrf_exempt
def get_features(request):
  data = {}
  allGeojson = {}
  featureType = request.POST.get('type', '')

  if featureType == "trees":
    for tree in Trees.objects.all(): 
      if tree.geojson == "": 
        continue
      data[tree.common_name] = {'geojson': tree.geojson}
  elif featureType == "stones":
    for stone in Stones.objects.all(): 
      if stone.geojson == "": 
        continue

      attributes = {}
      attributes['geojson'] = stone.geojson

      # Translate BCE/BC to negatives and AD/CE to positives for use by Mapbox's filters
      if stone.start_date != "": 
        start_date = numeric_date(stone.start_date)
        if start_date is not None: 
          attributes['start_date'] = start_date
      if stone.end_date != "": 
        end_date = numeric_date(stone.end_date)
        if end_date is not None: 
          attributes['end_date'] = end_date
      data[stone.name] = attributes

  return JsonResponse(data)

# Turns a date string into a numeric value, with BCE/BC represented as negative
def numeric_date(strDate):
  try: 
    strDate = str(strDate)
    intDate = int(re.sub("[^0-9]", "", strDate))
    if re.search("B\.?C\.?", strDate):
      intDate = -intDate
    return intDate
  except: 
    return None

# Returns information about the requested search result
@csrf_exempt
def result_info(request):
  itemName = request.POST.get('itemName', '')
  itemType = request.POST.get('itemType', '')
  
  # Filter is used rather than get in order to allow use of the values() function 
  attributes = {}
  if itemType == 'trees':
    tree = Trees.objects.filter(common_name=itemName)
    attributes = list(tree.values())[0]
  elif itemType == 'stones':
    stone = Stones.objects.filter(name=itemName)
    attributes = list(stone.values())[0]

  # Get associated image urls if they exist 
  image_urls = []
  if itemType == 'trees':
    images = TreeImages.objects.filter(tree__common_name=itemName)
    for image in images: 
      image_urls.append(image.img.url)
  elif itemType == 'stones':
    images = StoneImages.objects.filter(stone__name=itemName)
    for image in images: 
      image_urls.append(image.img.url)

  attributes['image_urls'] = image_urls

  # Clear values that we don't want to display
  if 'geojson' in attributes: 
    del attributes['geojson']
  if 'id' in attributes: 
    del attributes['id']

  addUnitsOfMeasurement(attributes)
  
  return JsonResponse(attributes)

# Add units of measurement to attributes where appropriate 
def addUnitsOfMeasurement(attributes): 
  for attr in attributes:
    if attributes[attr] == None or attributes[attr] == "":
      continue

    units = ""
    if "density" in attr: 
      units = " kg/m^3"
    elif "elastic" in attr: 
      units = " kg/cm^2"
    elif "strength" in attr or "rupture" in attr: 
      units = " MPa"
    elif "absorption" in attr: 
      units = "%"

    if units != "":
      val = str(attributes[attr])
      val += units
      attributes[attr] = val

class TreeForm(forms.ModelForm):
  citation = forms.FileField(required=False)
  class Meta: 
    model = Trees
    fields = ['common_name', 'sci_name', 'distribution', 'rot_resistance', 'workability', 
            'common_uses', 'notes', 'tree_height_low', 'tree_height_high', 'tree_rad_low', 'tree_rad_high', 'density',
            'janka_hardness', 'rupture_modulus', 'crushing_strength', 'shrink_rad', 'shrink_tan', 
            'shrink_volumetric', 'citation']

class TreeUpdate(UpdateView):
  model = Trees
  # Any changes to fields will need to include a corresponding attribute in the TreeEdits model
  form_class = TreeForm
  template_name = 'tree/trees-form.html'

  def form_valid(self, form):
    edit = TreeEdits()
    tree = Trees.objects.get(pk=self.object.pk)

    attrChanged = False
    for attr in form.cleaned_data: 
      if hasattr(edit, attr) and not hasattr(tree, attr):
        setattr(edit, attr, form.cleaned_data[attr])
      elif hasattr(tree, attr) and hasattr(edit, attr):
        if getattr(tree, attr) != form.cleaned_data[attr]:
          setattr(edit, attr, form.cleaned_data[attr])
          attrChanged = True 

    if attrChanged: 
      edit.tree = tree
      edit.save()

    return HttpResponseRedirect(self.get_success_url())

class StoneForm(forms.ModelForm):
  citation = forms.FileField(required=False)
  class Meta: 
    model = Stones 
    fields = ['name', 'alternate_name', 'age', 'appearance', 'poisson_ratio_low', 'poisson_ratio_high',
            'absorption', 'quarry_location', 'notes', 'dates_of_use', 'start_date', 'end_date', 'dates_notes', 
            'density_low', 'density_high', 'elastic_modulus_average', 'elastic_modulus_low', 'elastic_modulus_high',
            'rupture_modulus_average', 'rupture_modulus_low', 'rupture_modulus_high', 'compressive_strength_average', 
            'compressive_strength_high', 'compressive_strength_high']

class StoneUpdate(UpdateView):
  model = Stones 
  form_class = StoneForm
  template_name = 'tree/stones-form.html'

  def form_valid(self, form):
    edit = StoneEdits()
    stone = Stones.objects.get(pk=self.object.pk)

    attrChanged = False
    for attr in form.cleaned_data: 
      if not hasattr(stone, attr) and hasattr(edit, attr):
        setattr(edit, attr, form.cleaned_data[attr])
        attrChanged = True
      elif hasattr(stone, attr) and hasattr(edit, attr):
        if getattr(stone, attr) != form.cleaned_data[attr]:
          setattr(edit, attr, form.cleaned_data[attr])
          attrChanged = True 

    if attrChanged: 
      edit.stone = stone
      edit.save()

    return HttpResponseRedirect(self.get_success_url())

class EditListView(LoginRequiredMixin, ListView):
  model = TreeEdits
  template_name = 'tree/edits-list.html'
  context_object_name = 'tree_edits_list'

  def get_context_data(self, **kwargs):
    context = super(EditListView, self).get_context_data(**kwargs)
    context.update({
      'stone_edits_list': StoneEdits.objects.order_by('name')
    })
    return context

class TreeEditApproveView(DetailView):
  model = TreeEdits
  template_name = 'tree/edit.html'
  context_object_name = 'edit_object'

  def get_context_data(self, **kwargs): 
    context = super(TreeEditApproveView, self).get_context_data(**kwargs)
    edit = context['edit_object']
    context.update({
      'object': model_to_dict(edit.main_object),
      'edit_object': model_to_dict(edit.main_object)
    })
    return context