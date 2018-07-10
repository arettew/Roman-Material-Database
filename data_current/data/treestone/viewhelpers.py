from treestone.tree.models import Stones
from treestone.tree.models import Trees
from treestone.tree.models import StoneImages 
from treestone.tree.models import TreeImages 
from treestone.tree.models import TreeEdits 
from treestone.tree.models import StoneEdits

from django.core.mail import send_mail 

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
    return None

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
# Helpers for TreeUpdateView/StoneUpdateView
# -----------------------------------------------------------------------

# Create a TreeEdit or StoneEdit object from form data 
def createEdit(material_type, main_object, data, user):
  if not (material_type == 'trees' or material_type == 'stones'):
    return 
  edit = TreeEdits() if material_type == "trees" else StoneEdits()

  attrChanged = False
  for attr in data: 
    if hasattr(edit, attr) and not hasattr(main_object, attr): 
      setattr(edit, attr, data[attr])
    elif hasattr(main_object, attr) and hasattr(edit, attr):
      if getattr(main_object, attr) != data[attr]:
        setattr(edit, attr, data[attr])
        attrChanged = True
  
  if attrChanged: 
    edit.main_object = main_object
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
  attributes = sorted(edit_object_dict)
  for attr in attributes: 
    if not attr in object_dict.keys(): 
      attributes.remove(attr)
  try: 
    attributes.remove('id')
  except: 
    pass

  context.update({
    'object': object_dict,
    'edit_object': edit_object_dict,
    'attributes': attributes,
    'citation': citation,
    'type': materialType
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

    fieldObjects = StoneEdits._meta.get_fields() if materialType == 'stones' else TreeEdits._meta.get_fields()
    for fieldObjects in fieldObjects: 
      field = fieldObjects.name 
      # Don't want to affect id of the original object
      if field == 'id':
        continue
      if hasattr(mainObject, field) and getattr(edit, field):
        setattr(mainObject, field, getattr(edit, field))
   
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
    # EMAIL THAT MATCHES THE EMAIL IN SETTINGS HERE,
    [email],
    fail_silently=True,
  )