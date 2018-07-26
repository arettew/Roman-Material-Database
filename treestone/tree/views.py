from django.shortcuts import render

import csv, re, json, os

from django import forms
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader

#django generic class view 
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import FormView, UpdateView, CreateView

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm

#from treestone.tree.models import the model that you are using in model = MyModel
from treestone.tree.models import Stones, StoneImages, StoneEdits
from treestone.tree.models import Trees, TreeImages, TreeEdits
from django.contrib.auth.models import User

# Import helper functions for the CBVs 
import viewhelpers as helper

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

# The view that controls the home page 
class HomeView(TemplateView):
  template_name = "tree/home.html"

# Form to register for the site 
class SignupForm(UserCreationForm):
  email = forms.EmailField()

# View that controls the registration page 
class RegisterView(FormView):
  form_class = SignupForm
  template_name = 'registration/register.html'

  # Saves user if the SignupForm is valid 
  def form_valid(self, form):
    username = form.cleaned_data["username"]
    password = form.cleaned_data["password1"]
    email = form.cleaned_data["email"]

    user = User.objects.create_user(username, email, password)
    user.save()

    # log in user 
    user = authenticate(username=username, password=password)
    login(self.request, user)

    return HttpResponseRedirect("/")


# The view that controls the main database page 
class MapView(TemplateView):
  template_name = 'tree/map.html'

# Returns the GeoJSON for database entires, with featureType differentiating between trees 
# and stones 
@csrf_exempt
def get_features(request):
  data = {}
  allGeojson = {}
  featureType = request.POST.get('type', '')

  if featureType == "trees":
    for tree in Trees.objects.all(): 
      if not tree.geojson: 
        continue
      data[tree.common_name] = {'geojson': tree.geojson}
  elif featureType == "stones":
    for stone in Stones.objects.all(): 
      if not stone.geojson: 
        continue

      attributes = {}
      attributes['geojson'] = stone.geojson

      # Translate BCE/BC to negatives and AD/CE to positives for use by Mapbox's filters
      if stone.start_date: 
        start_date = helper.numericDate(stone.start_date)
        if start_date: 
          attributes['start_date'] = start_date
      if stone.end_date: 
        end_date = helper.numericDate(stone.end_date)
        if end_date: 
          attributes['end_date'] = end_date
      data[stone.name] = attributes

  return JsonResponse(data)

# Returns information about the requested search result
@csrf_exempt
def result_info(request):
  itemName = request.POST.get('itemName', '')
  itemType = request.POST.get('itemType', '')
  
  # Filter is used rather than get in order to allow use of the values() function 
  data = {}
  result = Trees.objects.filter(common_name=itemName) if itemType == "trees" else Stones.objects.filter(name=itemName)
  attributes = list(result.values())[0]
  pk = result[0].pk
  data['pk'] = pk

  # Get associated image urls if they exist 
  imageUrls = helper.getImages(pk, itemType)
  data['image_urls'] = imageUrls

  # Clear values that we don't need
  del attributes['geojson']
  del attributes['id']

  # Is there a user logged in? 
  data['user'] = True if request.user.is_authenticated() else False

  helper.addUnitsOfMeasurement(attributes)
  data['attributes'] = attributes

  return JsonResponse(data)

# Return a geojson file based on the materialType (trees or stones) and pk specified in the URL
@csrf_exempt 
def get_geojson_file(request, **kwargs):
  materialType = kwargs['type']
  pk = kwargs['pk']
  try: 
    item = helper.getObject(materialType, pk)
  except: 
    return HttpResponse(status=404)
    
  response = HttpResponse(content_type='text/geojson')
  response['Content-Disposition'] = "attachment; filename='" + str(item) + ".geojson'" 
  json.dump(json.loads(item.geojson), response)
  return response

# The form used for objects related to Trees 
class TreeForm(forms.ModelForm):
  citation = forms.FileField(required=False)
  geojson_file = forms.FileField(required=False)
  #image = forms.ImageField(required=False)

  def __init__(self, *args, **kwargs):
    super(TreeForm, self).__init__(*args, **kwargs)
    self.fields['common_name'].required = True

  class Meta: 
    model = Trees
    fields = ['common_name', 'sci_name', 'distribution', 'rot_resistance', 'workability', 
            'common_uses', 'notes', 'tree_height_low', 'tree_height_high', 'tree_rad_low', 'tree_rad_high', 'density',
            'janka_hardness', 'rupture_modulus', 'crushing_strength', 'shrink_rad', 'shrink_tan', 
            'shrink_volumetric', 'geojson_file', 'citation']
  
  # Makes sure that the geojson uploaded is valid 
  def clean_geojson_file(self):
    geojsonFile = self.cleaned_data["geojson_file"]
    helper.validateGeojson(self, geojsonFile)

# The form used for objects related to Stones
class StoneForm(forms.ModelForm):
  citation = forms.FileField(required=False)
  geojson_file = forms.FileField(required=False)
  #image = forms.ImageField(required=False)

  def __init__(self, *args, **kwargs):
    super(StoneForm, self).__init__(*args, **kwargs)
    self.fields['name'].required = True

  class Meta: 
    model = Stones 
    fields = ['name', 'alternate_name', 'age', 'appearance', 'poisson_ratio_low', 'poisson_ratio_high',
            'absorption', 'quarry_location', 'notes', 'dates_of_use', 'start_date', 'end_date', 'dates_notes', 
            'density_low', 'density_high', 'elastic_modulus_average', 'elastic_modulus_low', 'elastic_modulus_high',
            'rupture_modulus_average', 'rupture_modulus_low', 'rupture_modulus_high', 'compressive_strength_average', 
            'compressive_strength_high', 'compressive_strength_high', 'geojson_file', 'citation']
  
  # Makes sure that the geojson uploaded is valid 
  def clean_geojson_file(self):
    geojsonFile = self.cleaned_data["geojson_file"]
    helper.validateGeojson(self, geojsonFile)

class TreeCreateView(LoginRequiredMixin, CreateView):
  model = Trees
  form_class = TreeForm 
  template_name = 'tree/update-form.html'

  def form_valid(self, form):
    helper.createNewObjectEdit('trees', form.cleaned_data, self.request.user)
    return HttpResponseRedirect('/')

class StoneCreateView(LoginRequiredMixin, CreateView):
  model = Stones
  form_class = StoneForm 
  template_name = 'tree/update-form.html'

  def form_valid(self, form):
    helper.createNewObjectEdit('stones', form.cleaned_data, self.request.user)
    return HttpResponseRedirect('/')

# The view which is used to submit updates to tree objects 
class TreeUpdateView(LoginRequiredMixin, UpdateView):
  model = Trees
  # Any changes to fields will need to include a corresponding attribute in the TreeEdits model
  form_class = TreeForm
  template_name = 'tree/update-form.html'

  def form_valid(self, form):
    tree = Trees.objects.get(pk=self.object.pk)
    helper.createEdit('trees', tree, form.cleaned_data, self.request.user)
    return HttpResponseRedirect(self.get_success_url())

# The view which is used to submit updates to stone objects
class StoneUpdateView(LoginRequiredMixin, UpdateView):
  model = Stones 
  form_class = StoneForm
  template_name = 'tree/update-form.html'

  def form_valid(self, form):
    edit = StoneEdits()
    stone = Stones.objects.get(pk=self.object.pk)
    helper.createEdit('stones', stone, form.cleaned_data, self.request.user)

    return HttpResponseRedirect(self.get_success_url())

# The view which displays a list of all proposed edits 
class EditListView(UserPassesTestMixin, LoginRequiredMixin, ListView):
  model = TreeEdits
  template_name = 'tree/edits-list.html'
  context_object_name = 'tree_edits_list'

  def test_func(self): 
    return self.request.user.is_staff

  def get_context_data(self, **kwargs):
    context = super(EditListView, self).get_context_data(**kwargs)
    context.update({
      'stone_edits_list': StoneEdits.objects.order_by('name')
    })
    return context

# The view which is used to approve edits to objects related to Trees
class TreeEditApproveView(UserPassesTestMixin, LoginRequiredMixin, DetailView):
  model = TreeEdits
  template_name = 'tree/edit-approve.html'
  context_object_name = 'edit_object'

  def test_func(self): 
    return self.request.user.is_staff

  def get_context_data(self, **kwargs): 
    context = super(TreeEditApproveView, self).get_context_data(**kwargs)
    return helper.createContext(context, "trees")

  def post(self, request, pk): 
    url = helper.processDecision(request, pk, "trees")
    return HttpResponseRedirect(url)

# THe view which is used to approve edits to objects related to stones 
class StoneEditApproveView(UserPassesTestMixin, LoginRequiredMixin, DetailView): 
  model = StoneEdits
  template_name = 'tree/edit-approve.html'
  context_object_name = 'edit_object'

  def test_func(self): 
    return self.request.user.is_staff
    
  def get_context_data(self, **kwargs): 
    context = super(StoneEditApproveView, self).get_context_data(**kwargs)
    return helper.createContext(context, "stones")

  def post(self, request, pk): 
    url = helper.processDecision(request, pk, "stones")
    return HttpResponseRedirect(url)

# Get the edit geoJSON and the main object geoJSON for a edit approval page
@csrf_exempt
def approve_geojson(request):
  pk = request.POST.get('pk', '')
  materialType = request.POST.get('type', '')
  edit = helper.getEdit(materialType, pk)

  data = {}
  data['editGeojson'] = edit.geojson
  data['mainObjectGeosjon'] = edit.main_object.geojson if edit.main_object else ""

  return JsonResponse(data)

# The form used when a staff user rejects an edit
class RejectForm(forms.Form): 
  reason = forms.CharField(widget=forms.Textarea)

# The view that controls the rejection form 
class RejectView(FormView):
  form_class = RejectForm
  template_name = 'tree/reject.html'

  def get(self, request, **kwargs):
    # If this doesn't match a type and edit, return a 404 response
    materialType = self.kwargs['type']
    pk = self.kwargs['pk']
    if not materialType == 'trees' and not materialType == 'stones':
      return HttpResponse(status=404)
    try:
      edit = helper.getEdit(materialType, pk)
    except: 
      return HttpResponse(status=404)

    form = RejectForm()
    return self.render_to_response(self.get_context_data(form=form))

  def form_valid(self, form): 
    materialType = self.kwargs['type']
    pk = self.kwargs['pk']
    edit = helper.getEdit(materialType, pk)

    helper.sendRejection(edit, form.cleaned_data)
    edit.delete()

    return HttpResponseRedirect('/edits-list/')

