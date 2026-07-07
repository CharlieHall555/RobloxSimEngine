import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from evaluation.DataModelGenerator import *

test_dict = {
  "ClassName": "DataModel",
  "Children": [
    {
      "ClassName": "Workspace",
      "Children": [
        {
          "ClassName": "Part",
          "Properties": {"Name" : "Part1"}
        },
        {
          "ClassName": "Model",
          "Children": [
            {
              "ClassName": "Part"
            }
          ]
        }
      ]
    },
  ]
}

datamodel = generate_data_model(test_dict)

pretty_print(datamodel)