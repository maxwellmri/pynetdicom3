
# Version Number
__version__ = ['0', '1', '0']
pynetdicom_version = 'PYNETDICOM_' + ''.join(__version__)

# UID prefix provided by https://www.medicalconnections.co.uk/Free_UID
pynetdicom_uid_prefix = '1.2.826.0.1.3680043.9.3811.' + \
                                        '.'.join(__version__)

from pynetdicom3.applicationentity import ApplicationEntity as AE
from pynetdicom3.association import Association
from pynetdicom3.ACSEprovider import ACSEServiceProvider as ACSE
from pynetdicom3.DIMSEprovider import DIMSEServiceProvider as DIMSE
from pynetdicom3.DULprovider import DULServiceProvider as DUL
from pynetdicom3.SOPclass import STORAGE_CLASS_LIST as StorageSOPClassList
from pynetdicom3.SOPclass import QR_CLASS_LIST as QueryRetrieveSOPClassList
from pynetdicom3.SOPclass import VerificationSOPClass

# Set up logging system for the whole package.  In each module, set
# logger=logging.getLogger('pynetdicom') and the same instance will be
# used by all At command line, turn on debugging for all pynetdicom
# functions with: import netdicom netdicom.debug(). Turn off debugging
# with netdicom.debug(False)
import logging

# pynetdicom defines a logger with a NullHandler only.
# Client code have the responsability to configure
# this logger.
#logger = logging.getLogger('pynetdicom')
#logger.addHandler(logging.NullHandler())


# helper functions to configure the logger. This should be
# called by the client code.
def logger_setup():
    logger = logging.getLogger('pynetdicom')
    handler = logging.StreamHandler()
    logger.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(levelname).1s: %(message)s')
    #formatter = logging.Formatter("%(name)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # logging.getLogger('netdicom.FSM').setLevel(logging.CRITICAL)
    #logging.getLogger('pynetdicom.DUL').setLevel(logging.CRITICAL)


def debug(debug_on=True):
    """Turn debugging of DICOM network operations on or off."""
    logger = logging.getLogger('pynetdicom')
    logger.setLevel(logging.DEBUG)

#logger_setup()

