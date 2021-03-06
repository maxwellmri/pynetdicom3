#!/usr/bin/env python

"""
    A movescp application. 
"""

import argparse
import logging
import os
import socket
import sys
import time

from pydicom import read_file
from pydicom.dataset import Dataset
from pydicom.uid import ExplicitVRLittleEndian, ImplicitVRLittleEndian, \
    ExplicitVRBigEndian

from pynetdicom3 import AE, QueryRetrieveSOPClassList, StorageSOPClassList

logger = logging.Logger('movescp')
stream_logger = logging.StreamHandler()
formatter = logging.Formatter('%(levelname).1s: %(message)s')
stream_logger.setFormatter(formatter)
logger.addHandler(stream_logger)
logger.setLevel(logging.ERROR)

def _setup_argparser():
    # Description
    parser = argparse.ArgumentParser(
        description="The movescp application implements a Service Class "
                    "Provider (SCP) for the Query/Retrieve (QR) Service Class "
                    "and the Basic Worklist Management (BWM) Service Class. "
                    "movescp only supports query functionality using the C-MOVE "
                    "message. It receives query keys from an SCU and sends a "
                    "response. The application can be used to test SCUs of the "
                    "QR and BWM Service Classes.",
        usage="movescp [options] port")
        
    # Parameters
    req_opts = parser.add_argument_group('Parameters')
    req_opts.add_argument("port", 
                          help="TCP/IP port number to listen on", 
                          type=int)

    # General Options
    gen_opts = parser.add_argument_group('General Options')
    gen_opts.add_argument("--version", 
                          help="print version information and exit", 
                          action="store_true")
    gen_opts.add_argument("--arguments", 
                          help="print expanded command line arguments", 
                          action="store_true")
    gen_opts.add_argument("-q", "--quiet", 
                          help="quiet mode, print no warnings and errors", 
                          action="store_true")
    gen_opts.add_argument("-v", "--verbose", 
                          help="verbose mode, print processing details", 
                          action="store_true")
    gen_opts.add_argument("-d", "--debug", 
                          help="debug mode, print debug information", 
                          action="store_true")
    gen_opts.add_argument("-ll", "--log-level", metavar='[l]', 
                          help="use level l for the logger (fatal, error, warn, "
                               "info, debug, trace)", 
                          type=str, 
                          choices=['fatal', 'error', 'warn', 
                                   'info', 'debug', 'trace'])
    gen_opts.add_argument("-lc", "--log-config", metavar='[f]', 
                          help="use config file f for the logger", 
                          type=str)
    
    # Network Options
    net_opts = parser.add_argument_group('Network Options')
    net_opts.add_argument("-aet", "--aetitle", metavar='[a]etitle', 
                          help="set my AE title (default: MOVESCP)", 
                          type=str, 
                          default='MOVESCP')
    net_opts.add_argument("-to", "--timeout", metavar='[s]econds', 
                          help="timeout for connection requests", 
                          type=int,
                          default=0)
    net_opts.add_argument("-ta", "--acse-timeout", metavar='[s]econds', 
                          help="timeout for ACSE messages", 
                          type=int,
                          default=30)
    net_opts.add_argument("-td", "--dimse-timeout", metavar='[s]econds', 
                          help="timeout for DIMSE messages", 
                          type=int,
                          default=0)
    net_opts.add_argument("-pdu", "--max-pdu", metavar='[n]umber of bytes', 
                          help="set max receive pdu to n bytes", 
                          type=int,
                          default=16384)
    
    # Transfer Syntaxes
    ts_opts = parser.add_argument_group('Preferred Transfer Syntaxes')
    ts_opts.add_argument("-x=", "--prefer-uncompr",
                         help="prefer explicit VR local byte order (default)",
                         action="store_true")
    ts_opts.add_argument("-xe", "--prefer-little",
                         help="prefer explicit VR little endian TS",
                         action="store_true")
    ts_opts.add_argument("-xb", "--prefer-big",
                         help="prefer explicit VR big endian TS",
                         action="store_true")
    ts_opts.add_argument("-xi", "--implicit",
                         help="accept implicit VR little endian TS only",
                         action="store_true")

    return parser.parse_args()

args = _setup_argparser()

if args.verbose:
    logger.setLevel(logging.INFO)
    
if args.debug:
    logger.setLevel(logging.DEBUG)
    pynetdicom_logger = logging.getLogger('pynetdicom')
    pynetdicom_logger.setLevel(logging.DEBUG)

logger.debug('$movescp.py v%s %s $' %('0.1.0', '2016-04-12'))
logger.debug('')

# Validate port
if isinstance(args.port, int):
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        test_socket.bind((os.popen('hostname').read()[:-1], args.port))
    except socket.error:
        logger.error("Cannot listen on port %d, insufficient priveleges" 
            %args.port)
        sys.exit()

# Set Transfer Syntax options
transfer_syntax = [ImplicitVRLittleEndian,
                   ExplicitVRLittleEndian,
                   ExplicitVRBigEndian]

if args.implicit:
    transfer_syntax = [ImplicitVRLittleEndian]
    
if args.prefer_little:
    if ExplicitVRLittleEndian in transfer_syntax:
        transfer_syntax.remove(ExplicitVRLittleEndian)
        transfer_syntax.insert(0, ExplicitVRLittleEndian)

if args.prefer_big:
    if ExplicitVRBigEndian in transfer_syntax:
        transfer_syntax.remove(ExplicitVRBigEndian)
        transfer_syntax.insert(0, ExplicitVRBigEndian)

def on_c_move(dataset, move_aet):
    basedir = '../test/dicom_files/'
    dcm_files = ['CTImageStorage.dcm']
    dcm_files = [os.path.join(basedir, x) for x in dcm_files]
    
    # Number of matches
    yield len(dcm_files)
    
    # Address and port to send to
    if move_aet == b'ANY-SCP         ':
        yield '10.40.94.43', 104
    else:
        yield None, None
    
    # Matching datasets to send
    for dcm in dcm_files:
        data = read_file(dcm, force=True)
        yield data

# Create application entity
ae = AE(ae_title=args.aetitle,
        port=args.port,
        scu_sop_class=StorageSOPClassList, 
        scp_sop_class=QueryRetrieveSOPClassList,
        transfer_syntax=transfer_syntax)

ae.maximum_pdu_size = args.max_pdu

# Set timeouts
ae.network_timeout = args.timeout
ae.acse_timeout = args.acse_timeout
ae.dimse_timeout = args.dimse_timeout

ae.on_c_move = on_c_move

ae.start()
