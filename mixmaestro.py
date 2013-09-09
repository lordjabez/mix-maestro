"""
@copyright: 2013 Single D Software - All Rights Reserved
@summary: Main module for Mix Maestro.
"""


# Standard library imports
import logging
import sys

# Application imports
import httpserver


# Configure the logging module.
_logformat = '%(asctime)s : %(levelname)s : %(name)s : %(message)s'
logging.basicConfig(format=_logformat, level=logging.DEBUG)


# Initialize the mixer object depending on command line parameters.
if len(sys.argv) > 2 and sys.argv[1] == 'RolandVMixer':
    import rolandvmixer
    _mixer = rolandvmixer.RolandVMixer(sys.argv[2])
elif len(sys.argv) > 2 and sys.argv[1] == 'TestRolandVMixer':
    import testrolandvmixer
    _mixer = testrolandvmixer.TestRolandVMixer(sys.argv[2])
else:
    import genericmixer
    _mixer = genericmixer.GenericMixer()

# Start the application components
httpserver.start(_mixer)
