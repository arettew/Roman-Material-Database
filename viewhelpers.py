from treestone.tree.models import Stones
from treestone.tree.models import Trees
from treestone.tree.models import StoneImages 
from treestone.tree.models import TreeImages 
from treestone.tree.models import TreeEdits 
from treestone.tree.models import StoneEdits

from django.core.mail import send_mail 
from django.contrib.staticfiles.templatetags.staticfiles import static

from string import ascii_lowercase
import os

# -----------------------------------------------------------------------
# General purpose helper functions
# -----------------------------------------------------------------------

# Returns an edit object based on if materialType is "stones" or "trees"
def getEdit(materialType, pk):
  if materialType == 'stones':
    return StoneEdits.objects.get(pk=pk)
  elif materialType == 'trees':
    return TreeEdits.objects.get(pk=pk)
  else:
    raise ValueError("Invalid materialType")

# Returns an tree or stone object based on materialType
def getObject(materialType, pk):
  if materialType == 'stones': 
    return Stones.objects.get(pk=pk)
  elif materialType == 'trees': 
    return Trees.objects.get(pk=pk)
  else: 
    raise ValueError("Invalid materialType")

# -----------------------------------------------------------------------
# Helpers for get-features
# -----------------------------------------------------------------------
import re 

# Changes a string to a numeric date 
def numericDate(strDate):
  try: 
    strDate = str(strDate)
    intDate = int(re.sub("[^0-9]", "", strDate))
    if re.search("B\.?C\.?", strDate):
      intDate = -intDate
    return intDate
  except: 
    return None

# -----------------------------------------------------------------------
# Helpers for result-info
# -----------------------------------------------------------------------

# Get image urls from the item pk and item type ("stones" or "trees")
def getImages(pk, itemType): 
  imageUrls = []
  pathFromCwd = "treestone/tree/static/images/" + itemType + "/"
  pathFromStatic = "images/" + itemType + "/"

  try: 
    open(pathFromCwd + "AT" + str(pk) + ".jpg")
    imageUrls.append(static(pathFromStatic + "AT" + str(pk) + ".jpg"))
  except: 
    pass

  letters = ascii_lowercase[1:]
  for letter in letters: 
    try: 
      open(pathFromCwd + "AT" + str(pk) + letter + ".jpg")
      imageUrls.append(static(pathFromStatic + "AT" + str(pk) + letter + ".jpg"))
    except: 
      break
  
  return imageUrls

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

# -----------------------------------------------------------------------
# Helpers for forms (TreeForm/StoneForm)
# -----------------------------------------------------------------------
import geojson 

# Validate that a geoJSON file is valid for a TreeForm or StoneForm
def validateGeojson(self, geojsonFile): 
  if geojsonFile is None: 
    return 
  if not geojsonFile.name.endswith('.geojson') and not geojsonFile.name.endswith('.json'):
    self.add_error('geojson_file', "Illegal file type")
    return 
  
  geojsonString = geojsonFile.read()
  try: 
    geojsonObject = geojson.loads(geojsonString)
    if not geojsonObject.is_valid: 
      self.add_error('geojson_file', "Illegal GeoJSON")
  except: 
    self.add_error('geojson_file', "Illegal GeoJSON")

  self.cleaned_data["geojson"] = geojsonString

# -----------------------------------------------------------------------
# Helpers for TreeUpdateView/StoneUpdateView
# -----------------------------------------------------------------------

# Create a TreeEdit or StoneEdit object from form data 
def createEdit(materialType, mainObject, data, user):
  if not (materialType == 'trees' or materialType == 'stones'):
    return 
  edit = TreeEdits() if materialType == "trees" else StoneEdits()

  attrChanged = False
  for attr in data: 
    if hasattr(edit, attr) and not hasattr(mainObject, attr): 
      setattr(edit, attr, data[attr])
    elif hasattr(mainObject, attr) and hasattr(edit, attr):
      mainAttr = getattr(mainObject, attr)
      editAttr = data[attr]

      if isinstance(mainAttr, basestring): 
        mainAttr = mainAttr.strip()
        editAttr = editAttr.strip()

      if not mainAttr == editAttr:
        setattr(edit, attr, editAttr)
        attrChanged = True
  
  if attrChanged: 
    edit.main_object = mainObject
    edit.user = user
    edit.save()
  
  return

# -----------------------------------------------------------------------
# Helpers for TreeEditApproveView/StoneEditApproveView
# -----------------------------------------------------------------------
from django.forms.models import model_to_dict

# Create the context for the edit approval views 
def createContext(context, materialType): 
  edit = context['edit_object']
  object_dict = model_to_dict(edit.main_object)
  edit_object_dict = model_to_dict(edit)
  citation = edit_object_dict['citation']

  # List that will be used to display attributes 
  attributes = sorted(edit_object_dict.keys())
  for attr in attributes: 
    if not hasattr(edit.main_object, attr): 
      attributes.remove(attr)

  attributes.remove('id')
  attributes.remove('geojson')
  try: 
    attributes.remove('main_object')
  except: 
    pass

  # image_url = edit.image.url if edit.image else ""

  context.update({
    'object': object_dict,
    'edit_object': edit_object_dict,
    'attributes': attributes,
    'citation': citation,
    'type': materialType,
    #'image_url': image_url,
    'edit_pk': edit.pk
  })
  return context

# Handles an approve/reject decision made within the edit approval views based on material type ("stones"/"trees")
# Returns a redirect URL 
def processDecision(request, pk, materialType):
  if not materialType == 'stones' and not materialType == 'trees':
    return
  if request.POST['decision'] == 'reject': 
    url = '/' + materialType + '/approve/reject/' + pk + '/'
  elif request.POST['decision'] == 'approve':
    edit = StoneEdits.objects.get(pk=pk) if materialType == 'stones' else TreeEdits.objects.get(pk=pk)
    mainObject = edit.main_object

    # Save edit values over into the main database entry 
    fieldObjects = StoneEdits._meta.get_fields() if materialType == 'stones' else TreeEdits._meta.get_fields()
    for fieldObjects in fieldObjects: 
      field = fieldObjects.name 
      # Don't want to affect id of the original object
      if field == 'id':
        continue
      if hasattr(mainObject, field) and getattr(edit, field):
        setattr(mainObject, field, getattr(edit, field))
    
    # Save the image, if there is one 
    #if edit.image:
      #newImage = StoneImages() if materialType == "stones" else TreeImages()
      #newImage.img = edit.image
      #newImage.main_object = mainObject
      #newImage.save()

    mainObject.save()
    deleteEditObject(materialType, pk)
    url = '/edits-list/'
    
  
  return url

# Deletes an edit object based on materialType with the primary key pk
def deleteEditObject(materialType, pk):
  if materialType == 'stones': 
    StoneEdits.objects.get(pk=pk).delete()
  else: 
    TreeEdits.objects.get(pk=pk).delete()

# -----------------------------------------------------------------------
# Helpers for RejectView
# -----------------------------------------------------------------------

#  Send a rejection email for an edit based on the givenr reason by a staff member 
def sendRejection(edit, data): 
  email = edit.user.email 
  reason = data['reason']

  message = "Your edit to " + str(edit.main_object) + " has been rejected."
  message += "The reason given is: " + reason

  send_mail(
    'Roman Materials Database Edit Decision',
    message,
    'heritagestructureslab@gmail.com',
    [email],
    fail_silently=True,
  )