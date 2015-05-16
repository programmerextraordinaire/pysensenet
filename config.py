#
# config.py
#
# This file defines configuration variables for pysensenet.
#
# ----------------------- IMPORTANT -----------------------
#
# The "websitepath" below should point to your Sense/Net
# website installation folder. It is used as a relative
# path for the following expected configuration:
#
#  C:\
#  |
#  +--+ inetpub
#     |
#     +--+ sensenet           <== default websitepath
#        |
#        +--- bin             <== default referencepath
#        |
#        o--- web.config      <== fallback configpath
#
# pysensenet will fail to load until this is set correctly.
#
###########################################################

import os

websitepath = r"C:\Projects\AztechWeb\Source\AztechWeb"
referencepath = os.path.join(websitepath, "bin")
