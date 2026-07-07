from classes.meta_classes.datamodel import Datamodel
from classes.roblox_classes import Instance
from classes.roblox_classes import class_mappings
 
default_data_model = {
  "ClassName": "DataModel",
  "Children": [
    {
      "ClassName": "Workspace",
      "Children": []
    },
  ]
}

def pretty_print(instance: Instance, indent: int = 0):
    indent_str = "  " * indent
    print(f"{indent_str}{instance.__class__} (Name: {getattr(instance, 'name', 'noname')})")

    for child in instance.children.all():
        pretty_print(child, indent + 1)

def load_object(parent : Instance , object_to_load : dict):
    class_name = object_to_load.get("ClassName" , "") 


    constructor = class_mappings.get(class_name , Instance)
    new : Instance = constructor()
    parent.add_child(new)

    properties = object_to_load.get("Properties" , {})

    for property_name , property_value in properties.items():
        print(property_name, property_value)
        if new.has_key(property_name):
            new.set_value(property_name , property_value)
            print("set")

    for each in object_to_load.get("Children" , []):
        load_object(new , each)

   
def generate_data_model(data_model : dict) -> Datamodel:
    root = Datamodel()
    
    for each in data_model.get("Children" , []):
        load_object(root , each)
        
    return root

