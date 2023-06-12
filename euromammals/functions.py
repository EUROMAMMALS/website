#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 12:35:34 2021

@author: lucadelu
"""
import os
import urllib.request
import tempfile
import zipfile
# import json
import base64
from PIL import Image
from PIL import ExifTags
from datetime import date
from datetime import datetime
from datetime import time
from decimal import Decimal
# from shapely.geometry import shape

from django.db.models.fields import IntegerField
from django.db.models.fields import AutoField
from django.db.models.fields import BooleanField
from django.db.models.fields import DecimalField
from django.db.models.fields import DateTimeField
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.related import ManyToManyField
from django.db import connection, transaction
from django.contrib.gis.db.models import GeometryField
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import MultiPoint
from django.contrib.gis.geos import MultiLineString
from django.contrib.gis.geos import MultiPolygon
from django.core.files import File
# from pyproj import CRS
# from pyproj.aoi import AreaOfInterest
# from pyproj.database import query_utm_crs_info

TMPDIR = tempfile.gettempdir()


def change_mutable(request, key, val):
    """Function to change the data of a request"""
    _mutable = request.data._mutable
    request.data._mutable = True
    request.data[key] = val
    request.data._mutable = _mutable
    return request


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, time):
        return str(obj)
    if isinstance(obj, Decimal):
        return "{}".format(obj)
    raise TypeError("Type %s not serializable" % type(obj))


def get_bool_value(field):
    """Function to return boolean value"""
    val = get_int_value(field)
    if val == 1:
        val = True
    elif val == 0:
        val = False
    else:
        val = None
    return val


def get_int_value(field):
    """Function to return integer value"""
    try:
        val = int(field)
    except:
        val = None
    return val


def get_decimal_value(field):
    """Function to return integer value"""
    try:
        val = float(field)
    except:
        val = None
    return val


def get_datetime(field):
    """Function to return datetime value"""
    if field == "":
        return None
    try:
        dateobj = datetime.strptime(field, "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            dateobj = datetime.strptime(field, "%d/%m/%Y %H:%M")
        except:
            try:
                if "." in field:
                    sfi = field.split(".")
                    if len(sfi[1]) > 7:
                        field = f"{sfi[0]}.{sfi[1][:6]}"
                        if "Z" in sfi[1]:
                            field += "Z"
                dateobj = datetime.strptime(field, "%Y-%m-%dT%H:%M:%S.%fZ")
            except:
                raise ValueError("Date time format not supported")
    return dateobj


def get_geometry(field, col):
    if isinstance(field, GEOSGeometry):
        geom = field
    elif isinstance(field, str) or isinstance(field, dict):
        geom = GEOSGeometry(str(field))
    if geom.geom_type.upper() == col.geom_type.upper():
        return geom
    elif geom.geom_type.upper() in col.geom_type.upper():
        if col.geom_type.upper() == "MULTIPOINT":
            return MultiPoint([geom])
        elif col.geom_type.upper() == "MULTILINESTRING":
            return MultiLineString([geom])
        elif col.geom_type.upper() == "MULTIPOLYGON":
            return MultiPolygon([geom])
    else:
        return None


def for_cols(cols, names, skipcsv=False):
    """For loop to check if all values are in a list"""
    err = []
    for col in cols:
        if col not in names:
            if skipcsv and col not in ["id", "geom"]:
                err.append(col)
            elif not skipcsv:
                err.append(col)
    return err


def check_columns(cols, model):
    """Check if all columns exists in the model"""
    names = [f.name for f in model._meta.get_fields()]
    err = for_cols(cols, names)
    if len(err) == 1:
        raise Exception("The column '{cols}' does not exist".format(cols=err[0]))
    elif len(err) > 1:
        raise Exception("The columns '{cols}' do not exist".format(cols=", ".join(err)))
    return True


def check_model_field(fields, key, val):
    """Check the type of input field and return the right value"""
    if key not in fields.keys():
        return None
    if isinstance(fields[key], ForeignKey):
        if val:
            if isinstance(val, int):
                return fields[key].related_model.objects.get(id__exact=val)
            elif isinstance(val, str):
                return fields[key].related_model.objects.get(name__exact=val)
            else:
                return None
    elif isinstance(fields[key], IntegerField) or isinstance(fields[key], AutoField):
        inval = get_int_value(val)
        if inval is not None:
            return inval
    elif isinstance(fields[key], BooleanField):
        inval = get_bool_value(val)
        if inval is not None:
            return inval
    elif isinstance(fields[key], DecimalField):
        inval = get_decimal_value(val)
        if inval is not None:
            return inval
    elif isinstance(fields[key], DateTimeField):
        inval = get_datetime(val)
        if inval is not None:
            return inval
    elif isinstance(fields[key], GeometryField):
        inval = get_geometry(val, fields[key])
        if inval is not None:
            return inval
    else:
        if val:
            return val
    return None


def create_geojson(feat, model, modify=False):
    errors = []
    warnings = []
    fields = {}
    for fi in model._meta.get_fields():
        fields[fi.name] = fi
    data = {}
    for key, val in feat["properties"].items():
        newval = check_model_field(fields, key, val)
        if newval is not None:
            data[key] = newval
        else:
            warnings.append("WARNING problem with {} property. ".format(key))
    if len(data.keys()) == 0:
        errors.append("ERROR no valid properties. ")
        return [False, warnings, errors]
    geom = check_model_field(fields, "geom", feat["geometry"])
    if geom is not None:
        data["geom"] = geom
    else:
        errors.append("ERROR no valid geometry")
    final = model(**data)
    if modify:
        try:
            final.save()
        except Exception as e:
            errors.append("ERROR saving the data: {}. ".format(e))
    else:
        try:
            final.save(force_insert=True)
        except Exception as e:
            errors.append("ERROR saving the data {}. ".format(e))
    if len(errors) == 0:
        return [True, warnings, errors]
    else:
        return [False, warnings, errors]


def read_csv(lines, model, sep="|", modify=False):
    """Add new data from CSV lines"""
    errors = []
    header = lines[0].decode().strip().lower().split(sep)
    fields = {}
    for fi in model._meta.get_fields():
        fields[fi.name] = fi
    try:
        check_columns(header, model)
    except Exception as e:
        raise (e)
    row = 2
    for line in lines[1:]:
        try:
            vals = line.decode().strip().split(sep)
        except:
            vals = line.decode("latin2").strip().split(sep)
        if not vals:
            continue
        samples = {}
        errs = []
        many = {}
        for i in range(len(vals)):
            try:
                k = header[i]
            except:
                errs.append(
                    "list index {nu} out of range of header, please "
                    "check the csv file with text editor and check "
                    "for extra pipes |".format(nu=i)
                )
            v = vals[i]
            # TODO replace with check_model_field function
            if isinstance(fields[k], ForeignKey):
                if v:
                    if v.isdigit():
                        key = fields[k].related_model.objects.filter(id__exact=v)
                    elif isinstance(v, str):
                        key = fields[k].related_model.objects.filter(name__exact=v)
                    else:
                        key = []
                    if len(key) == 1:
                        samples[k] = key[0]
                    else:
                        errs.append(f"Value {v} not found in field {k}")
            elif isinstance(fields[k], ManyToManyField):
                if v:
                    many[k] = []
                    for item in v.split(","):
                        if item.isdigit():
                            key = fields[k].related_model.objects.filter(id__exact=item)
                        elif isinstance(item, str):
                            key = fields[k].related_model.objects.filter(name__exact=item)
                        else:
                            key = []
                        if len(key) == 1:
                            many[k].append(key[0])
                        else:
                            errs.append(f"Value {item} not found in field {k}")
            elif isinstance(fields[k], IntegerField) or isinstance(
                fields[k], AutoField
            ):
                inval = get_int_value(v)
                if inval is not None:
                    samples[k] = inval
                else:
                    errs.append(f"Impossible get value {v} for field {fields[k]}")
            elif isinstance(fields[k], BooleanField):
                inval = get_bool_value(v)
                if inval is not None:
                    samples[k] = inval
                else:
                    errs.append(f"Impossible get value {v} for field {fields[k]}")
            elif isinstance(fields[k], DecimalField):
                inval = get_decimal_value(v)
                if inval is not None:
                    samples[k] = inval
                else:
                    errs.append(f"Impossible get value {v} for field {fields[k]}")
            elif isinstance(fields[k], DateTimeField):
                inval = get_datetime(v)
                if inval is not None:
                    samples[k] = inval
                else:
                    errs.append(f"Impossible get value {v} for field {fields[k]}")
            else:
                if v:
                    samples[k] = v
        if len(errs) > 0:
            errors.append({"id": row, "errors": errs})
        else:
            sam = model(**samples)
            if modify:
                try:
                    sam.save()
                except Exception as e:
                    errors.append(
                        {
                            "id": row,
                            "simpleerror": e,
                        }
                    )
                if len(many.items()) > 0:
                    for key, value in many.items():
                        try:
                            fi = getattr(sam, key)
                        except AttributeError:
                            continue
                        fi.set(value)
            else:
                try:
                    sam.save(force_insert=True)
                except Exception as e:
                    errors.append(
                        {
                            "id": row,
                            "simpleerror": e,
                        }
                    )
                if len(many.items()) > 0:
                    for key, value in many.items():
                        try:
                            fi = getattr(sam, key)
                        except AttributeError:
                            continue
                        fi.set(value)
        row += 1
    updateseqquery = (
        "SELECT setval(pg_get_serial_sequence('{table}', '{id}')"
        ", (SELECT MAX({id}) FROM {table}));".format(
            table=model._meta.db_table, id=model._meta.auto_field.name
        )
    )
    cursor = connection.cursor()
    with transaction.atomic():
        cursor.execute(updateseqquery)
    return errors


class geo_mapping:
    """This class is useful to import geodata into models"""

    def __init__(self, model, mapping):
        self.path = None
        self.model = model
        self.mapping = mapping
        self.downloaded = False

    def set_path(self, path):
        if os.path.exists(path):
            self.path = path
        else:
            raise Exception("Path {} doesn't exist".format(self.path))

    def download(self, url):
        tmpf = tempfile.NamedTemporaryFile()
        fname = tmpf.name
        tmpf.close()
        print(url, fname)
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )
        with urllib.request.urlopen(req) as resp, open(fname, "wb") as ouf:
            data = resp.read()  # a `bytes` object
            ouf.write(data)
            ouf.close()
        with zipfile.ZipFile(fname) as zipp:
            zipp.extractall(TMPDIR)
        os.remove(fname)
        self.downloaded = True

    def add(self):
        """"""
        try:
            lam = LayerMapping(self.model, self.path, self.mapping)
            lam.save()
        except Exception as err:
            print("Error importing data: {}".format(err))


# def django2shapely(infeature):
#     """
#     Convert GeoDjango feature in shapely object

#     Parameters:
#         infeature (obj): Django Model feature with geometry field

#     Returns:
#         shapely geometry
#     """
#     data = json.loads(infeature.geom.geojson)
#     return shape(data)


# def utm_from_extent(extent):
#     """Return the right UTM code from Django geometry envelope

#     Args:
#         extent (obj): list or Envelope geometry in longitude and latitude (EPSG 4326)

#     Returns:
#         CRS object
#     """
#     utm_crs_list = query_utm_crs_info(
#         datum_name="WGS 84",
#         area_of_interest=AreaOfInterest(
#             west_lon_degree=extent[0],
#             south_lat_degree=extent[1],
#             east_lon_degree=extent[2],
#             north_lat_degree=extent[3],
#         ),
#     )
#     return CRS.from_epsg(utm_crs_list[0].code)


def imagetobase64(fip):
    """Function to convert image to base65

    Args:
        fp: Path to image file, could be relative but it is better full

    Returns:
        Image in base64 string format
    """
    try:
        fil = open(fip, "rb")
    except:
        return ""
    image = File(fil)
    data = base64.b64encode(image.read())
    fil.close()
    return data


def exiffromimage(img):
    """_summary_

    Args:
        img (obj): ImageField or path of image

    Returns:
        A dictionary with all EXIF
    """
    img = Image.open("img.jpg")
    exif_data = img._getexif()
    exif = {
        ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS
    }
    return exif
