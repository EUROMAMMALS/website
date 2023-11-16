#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 09:04:32 2021

@author: lucadelu
"""

import os
import sys
import json
import django
from django.apps import apps
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'euromammals.settings')
django.setup()

from core.models import Country
from euromammals.functions import geo_mapping

TMPDIR = tempfile.gettempdir()

world_mapping = {
    'name': 'NAME',
    'shortname': 'SOV_A3',
    'geom' : 'MULTIPOLYGON',
}
world_address = "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries_lakes.zip"

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Import geo data into'
                                     'database using LayerMapping')
    parser.add_argument('-p', '--path', dest='path', default=None,
                        help="Path to downloaded data")
    parser.add_argument('-r', '--remove', dest='remove', action='store_true',
                        help="Remove data after importing")
    parser.add_argument('-w', '--world', dest='world', action='store_true',
                        help='Import Sovereignty countries'
                             ' downloaded from Natural Earth')
    ownmapping = parser.add_argument_group("Required arguments for "
                                           "'own mapping'")

    ownmapping.add_argument('-c', '--model', dest='model', default=None,
                            help="Model name to import")
    ownmapping.add_argument("-a", "--app", dest="app", default=None,
                            help="App name for model to import")
    ownmapping.add_argument("-m", "--mapping", default=None,
                            help="Mapping dictionary for the model to import"
                                 " in a JSON file")
    args = parser.parse_args()


    if args.world:
        mapping = geo_mapping(Country, world_mapping)
        if args.path:
            mapping.set_path(args.path)
        else:
            print("Downloading World data")
            mapping.download(world_address)
            mapping.set_path(os.path.join(TMPDIR,
                                          'ne_10m_admin_0_countries_lakes.shp'))
    else:
        if not args.model:
            raise ValueError("--world or --model argument is required")
        if not args.path:
            raise ValueError("--path argument is required with 'own mapping'")
        model = apps.get_model(app_label=args.app, model_name=args.model)
        with open(args.mapping) as f:
            modelmapping = json.load(f)
        mapping = geo_mapping(model, modelmapping)
        mapping.set_path(args.path)
    print("Importing data")
    mapping.add()

    if args.remove:
        import glob
        if args.world:
            for mr in glob.glob1(TMPDIR, "ne_10m_admin_0_countries_lakes.*"):
                os.remove(os.path.join(TMPDIR, mr))

if __name__ == "__main__" and __package__ is None:
    main()
