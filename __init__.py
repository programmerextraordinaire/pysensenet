# -*- coding: utf-8 -*-

#
# pysensenet.py
#
# by Thane Plummer
#
# Distribution
#    CodePlex: pysensenet.codeplex.com
#    GitHub: github.com/programmerextraordinaire/pysensenet
#
# License: Apache v2.0
#         

"""
pysensenet library for IronPython
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Basic usage:

   >>> import pysensenet
   >>> sn = pysensenet.PySenseNet()
   Connecting to SenseNet...
   >>> sn.version()




:copyright: (c) 2014 by Thane Plummer.
:license: Apache v2.0, see LICENSE for more details.

"""

from __future__ import print_function

import clr
import os
import sys


# ----------------------- IMPORTANT -----------------------
# The "websitepath" below must point to your Sense/Net
# website installation folder to find all needed DLLs.
#
# pysensenet will fail to load until this is set correctly.
#
from config import websitepath # Default is r"C:\inetpub\sensenet"
from config import referencepath # Default is r"C:\inetpub\sensenet\bin"


def _validReferencepath(referencepath):
    for fname in ["Microsoft.Practices.Unity.dll",
                  "SenseNet.ContentRepository.dll",
                  "SenseNet.CorePortlets.dll",
                  "SenseNet.Messaging.dll",
                  "SenseNet.Portal.dll",
                  "SenseNet.Storage.dll",
                  "SenseNet.Workflow.dll",
                  "SenseNet.Workflow.Definitions.dll"]:
        if not os.path.isfile(os.path.join(referencepath, fname)):
            return False
    return True


try:
    if not _validReferencepath(referencepath): 
        print("Cannot find Sensenet DLLs in referencepath folder: {0}".format(referencepath))
        print("")
        print("Please edit the 'websitepath' variable in site-packages\\pysensenet\\config.py.")
        raise SystemError
    else:
        print("Validated Sense/Net referencepath.")
        print("referencepath={0}".format(referencepath))
        from . import pysensenet
        from pysensenet import *
except SystemError:
    print("Error loading pysensenet.")
    


# ----------------------- NOTE -----------------------
# Add any custom references to Content Handlers as shown commented below.
#
clr.AddReferenceToFileAndPath(r"C:\Projects\AztechWeb\Source\AztechWeb\bin\AztechWeb.dll")
import Aztec.Code as AC
import Aztec.Code.ContentHandlers as ACCH
