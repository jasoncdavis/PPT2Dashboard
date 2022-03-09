#!/usr/bin/env python

"""Creates a Dashboard from PPTX and dynamic data files

#                                                                      #
pptx2dashboard.py
Reads in a .pptx file and dynamic data file (as JSON), then generates 
a basic dashboard

Required inputs/variables:
    pptx_file (str): The file location of the pptx template
    data_file (str): The file location of the dynamic data to process

    Reads 'env.yaml' file for libreoffice executable location, web
    publishing directory, image directory, etc.

    env.yaml has the following sample
    key: value

Outputs:
    return_code (int): integer representation of the processing result
    return_string (str): textual description of the processing results

Version log:
v1      2022-0309   Initial Release
"""

# Module level "dunders" - Credits
__version__ = '1'
__author__ = 'Jason Davis - jadavis@cisco.com'
__license__ = "Cisco Sample Code License, Version 1.1 - " + \
    "https://developer.cisco.com/site/license/cisco-sample-code-license/"


# Imports
import argparse
from datetime import datetime
import logging
import os
import pwd
import sys
from zipfile import ZipFile
import json
import pathlib
import subprocess
import shutil


def get_runtime_args():
    """Get user inputs for runtime options
    Uses ArgumentParser to read user CLI inputs and arguments.
    Validates user inputs and requirements.
    :returns: args as user arguments
    """
    parser = argparse.ArgumentParser(description='Convert supplied .pptx and dynamic data files into webpage.')
    parser.add_argument('pptx_file', help='Filename of .pptx file used as input and template for conversion - provide full path, if not in project directory')
    parser.add_argument('data_file', help='Filename of data file used as dynamic values - provide full path, if not in project directory')
    parser.add_argument('--webName', help='Optional name for the webpage; if not supplied it will use the basename of the .pptx file. E.g. if your template file is template-mybuilding.pptx and you don\'t specify --webName,\nthen the webpage will be http://SITE/template-mybuilding.  If you\'d rather have a webpage name different from the .pptx filename, include --webName. ')
    l_args = parser.parse_args()

    if l_args.pptx_file == None:
        parser.print_help()

    return l_args

def read_config_file(metric):
    """Reads a YAML file that defines environmental parameters and settings

    Parameters
    ----------
    metric : str
        The metric (key) to retrieve a value from in the env.yaml file

    Returns
    -------
    value : str
        A string representing the metric value retrieved
    """
    import yaml

    with open("env.yaml", "r", encoding='UTF-8') as ymlfile:
        try:
            cfg = yaml.safe_load(ymlfile)
        except yaml.YAMLError as e:
            print(e)
    
    return cfg.get(metric)

def checkprerequisites(l_args):
    """Ensure prerequisites for the project are available - env.yaml, 
    binaries, etc. Reads the env.yaml file for environment settings.

    Parameters
    ----------
    l_args : str
        CLI arguments provided and checked by argparse, passed in
    Returns
    -------
    webpubdir : str
        A string representing the web publication directory - usually
        managed by Apache web server
    webimgdir : str
        A string representing the web image directory for PNGs, etc.
    """
    # Ensure project dependencies exists
    if not os.path.exists('./env.yaml'):
        logging.critical('Missing required file ./env.yaml')
        sys.exit('EXITING - Unable to find ./env.yaml')

    webpubdir = read_config_file('WebPubDir')
    webimgdir = read_config_file('WebImgDir')

    for i in [l_args.pptx_file, l_args.data_file, webpubdir, webimgdir]:
        if not os.path.exists(i):
            logging.critical(f'Missing required file or directory {i}')
            sys.exit(f'EXITING - Unable to find {i}')

    # Ensure the web publishing directories are writable by user/process
    # running Python script by dropping a test file in each directory
    for i in [webpubdir, webimgdir]:
        if not os.path.exists(i):
            logging.critical(f'Missing required file or directory {i}')
            sys.exit(f'EXITING - Unable to find {i}')
        try:
            with open(f'{i}/testfile', 'w') as file:
                file.write('test')
                file.close()
        except PermissionError as error:
            logging.critical(
                f'Cannot write to directory {i} - consider adding ' + \
                 'userid \'' + str(os.getegid()) + f'\' to the ' + \
                 'group with write permissions to {i}\nError ' + \
                 'reported was:\n{error}')
            sys.exit(f'EXITING - File handling error -\n{error}')
        except IOError as error: 
            # The file was not accessible for some other reason
            # Alert the user and exit since continuing is unnecessary
            logging.critical(f'File handling error -\n{error}')
            sys.exit(f'EXITING - File handling error -\n{error}')

    # Ensure image converter exists
    imgconv = read_config_file('ImageConverter')
    if not os.path.isfile(imgconv) and not os.access(imgconv, os.X_OK):
        logging.critical(f'Missing required image converter')
        sys.exit(f'EXITING - Unable to find image converter')

    return webpubdir, webimgdir

def unzip_pptx(pptx_file):
    """Unzip the incoming PPTX, if needed"""
    # Get basename without .pptx extension, then see if a directory 
    #   version of it already exists, if so we already have a template
    #   to work from and can move on, if not we need unzip
    # TO-DO: add a CLI flag to allow someone to overwrite/ignore 
    #     previous version?
    pptdir = pptx_file.replace('.pptx', '')
    if not os.path.exists(pptdir):
        # Do unzip
        with ZipFile(pptx_file, 'r') as zipObject:
            # Extract all the contents of zip file in different directory
            zipObject.extractall(pptdir)
            logging.info(f'File is unzipped in {pptdir} folder') 

def replace_placeholders(l_args):
    """Replace the placeholders in the slide1.xml file, part of the
       PPT directory structure"""
    pptdir = l_args.pptx_file.replace('.pptx', '')
    
    with open(f'{pptdir}/ppt/slides/slide1.xml') as slide1xml:
        slidexml_data = slide1xml.read()

        with open(l_args.data_file) as in_datafile:
            # returns JSON object as a dictionary
            in_jsondatafile = in_datafile.read()
            jsondata = json.loads(in_jsondatafile)
            
            # Iterate through the JSON list
            for key, value in jsondata.items():
                slidexml_data = slidexml_data.replace(key,str(value))
        
        with open(f'{pptdir}/ppt/slides/slide1.xml.new', 'w') as newslide1xml:
            newslide1xml.write(slidexml_data)

def repackage_ppt(pptx_file, webName):
    """Repackage the PPT file - rename files and recreate ZIP file"""
    pptdir = pptx_file.replace('.pptx', '')
    os.rename(f'{pptdir}/ppt/slides/slide1.xml', f'{pptdir}/ppt/slides/slide1.xml.orig')
    os.rename(f'{pptdir}/ppt/slides/slide1.xml.new', f'{pptdir}/ppt/slides/slide1.xml')

    directory = pathlib.Path(f'{pptdir}/')
    with ZipFile(f'{webName}.pptx', mode="w") as archive:
        for file_path in directory.rglob("*"):
            archive.write(file_path, arcname=file_path.relative_to(directory))

def convert_pptx2png(webName):
    """Use libreoffice Impress app to convert image from PPTX to PNG"""
    cmdoutput = subprocess.check_output(
        f'libreoffice --convert-to png {webName}.pptx',
        stderr=subprocess.STDOUT,
        shell=True)

    logging.info('Image conversion command output -\n' + \
        cmdoutput.decode('ascii'))

def create_simple_dashboard(webName, webpubdir, webimgdir):
    """Create a simple webpage by referencing the PNG as an image"""
    newpng = f'{webName}.png'
    relativeimgdir = webimgdir.replace(webpubdir, '')

    # Create webpage template - double escape HTML {} elements
    # f-string inject page refresh rate and image source
    webtemplate = f'''<!DOCTYPE html>
<html lang="en">
<head>
<title>Mobile Device Counts Dashboard</title>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="{read_config_file('webrefresh')}">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {{
  font-family: Arial, Helvetica, sans-serif;
}}
</style>
</head>
<body>
<img src="{relativeimgdir}/{newpng}" alt="Building image with wireless device counts">
</body>
</html>
'''
    htmlfile = f'{webName}.html'
    with open(htmlfile, 'w') as f:
        f.write(webtemplate)

def copy_files_to_webserver(webName, webpubdir, webimgdir):
    """Copy files to webserver publishing and image directories"""
    shutil.copy(f'{webName}.html', webpubdir)
    shutil.copy(f'{webName}.png', webimgdir)
    cmdoutput = subprocess.check_output('hostname -I',
        stderr=subprocess.STDOUT,
        shell=True)
    logging.info(
        f'Published dashboard to http://localhost/{webName}.html ' + \
        'and http://' + cmdoutput.decode('ascii').strip() + \
        f'/{webName}.html')


####### Function definitions above
########################################
####### Main function definition below

def main(args):
    """Main function"""

    start_time = datetime.now() # current date and time
    logging.info('Started program')

    webName = args.pptx_file.replace('.pptx', '') \
        if args.webName == None else args.webName

    # Run individual steps    
    webpubdir, webimgdir = checkprerequisites(args)
    unzip_pptx(args.pptx_file)
    replace_placeholders(args)
    repackage_ppt(args.pptx_file, webName)
    convert_pptx2png(webName)
    create_simple_dashboard(webName, webpubdir, webimgdir)
    copy_files_to_webserver(webName, webpubdir, webimgdir)

    difference = (datetime.now() - start_time)
    total_seconds = difference.total_seconds()
    logging.info(f'Ended program - total runtime {total_seconds} seconds.')

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s: %(message)s', \
        level=logging.INFO)
    args = get_runtime_args()
    main(args)