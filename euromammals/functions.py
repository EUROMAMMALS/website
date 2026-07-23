#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 12:35:34 2021

@author: lucadelu
"""

import json
import os
import urllib.request
import tempfile
import zipfile
import random

# import json
import base64
from isort import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from PIL import ExifTags
from datetime import date
from datetime import datetime
from datetime import time
from decimal import Decimal
import xml.etree.ElementTree as ET

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
from django.conf import settings
import psycopg2

# from pyproj import CRS
# from pyproj.aoi import AreaOfInterest
# from pyproj.database import query_utm_crs_info

from .sql_queries import QUERY_GPS_BOAR
from .sql_queries import QUERY_GPS_BOAR_RESEARCH_GROUP
from .sql_queries import QUERY_GPS_DEER_RESEARCH_GROUP
from .sql_queries import SQL_QUERIES_LYNX
from .sql_queries import QUERY_GPS_DEER
from .sql_queries import QUERY_METADATA
from .sql_queries import QUERY_METADATA_ID

TMPDIR = tempfile.gettempdir()


def _get_psycopg2_connection(dbname):
    db_default = settings.DATABASES["default"]
    try:
        conn = psycopg2.connect(
            host=db_default.get("HOST", "localhost"),
            port=db_default.get("PORT", "5432"),
            dbname=dbname,
            user=db_default.get("USER", ""),
            password=db_default.get("PASSWORD", ""),
        )
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False
    return conn


def is_datacurator(user):
    superuser = bool(user.is_superuser)
    if superuser:
        return True
    superuser = bool("Superdatacurator" in user.groups.values_list("name", flat=True))
    if superuser:
        return True
    return False


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
    except (ValueError, TypeError):
        val = None
    return val


def get_decimal_value(field):
    """Function to return integer value"""
    try:
        val = float(field)
    except (ValueError, TypeError):
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
        except ValueError:
            try:
                if "." in field:
                    sfi = field.split(".")
                    if len(sfi[1]) > 7:
                        field = f"{sfi[0]}.{sfi[1][:6]}"
                        if "Z" in sfi[1]:
                            field += "Z"
                dateobj = datetime.strptime(field, "%Y-%m-%dT%H:%M:%S.%fZ")
            except (ValueError, IndexError):
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
        except UnicodeDecodeError:
            vals = line.decode("latin2").strip().split(sep)
        if not vals:
            continue
        samples = {}
        errs = []
        many = {}
        for i in range(len(vals)):
            try:
                k = header[i]
            except Exception:
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
                            key = fields[k].related_model.objects.filter(
                                name__exact=item
                            )
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
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
            },
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
    except OSError:
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
    # exif_data = img._getexif()
    exif = {
        ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS
    }
    return exif


def captcha_challenge():
    """Function to be used in the captcha for form

    Returns:
        list: a list with the value to show and the challenge
    """
    challenge = ""
    response = ""
    for i in range(4):
        digit = random.randint(0, 9)
        challenge += str(digit)

    response = str(int(challenge) + 1)
    print(challenge, response)
    return challenge, response


def deployment_distribution_plot(dbname, output=None, research_group=False):
    """Function to create the plot of distribution of deployments per year

    Parameters:
        dbname (str): name of the database to connect to
        output (str): path to save the output plot

    Returns:
        list: a list with the value to show and the challenge
    """

    # Establish the psycopg2 connection
    conn = _get_psycopg2_connection(dbname)
    if research_group:
        if dbname in ("eurodeer_db", "eureddeer_db", "euroibex_db", "eurowildcat_db"):
            QUERY_GPS = QUERY_GPS_DEER_RESEARCH_GROUP
        elif dbname in ("euroboar_db"):
            QUERY_GPS = QUERY_GPS_BOAR_RESEARCH_GROUP
        elif dbname in ("eurolynx_db"):
            QUERY_GPS = SQL_QUERIES_LYNX
        else:
            print(f"Database {dbname} not recognized for GPS query.")
            return False
    else:
        if dbname in ("eurodeer_db", "eureddeer_db", "euroibex_db", "eurowildcat_db"):
            QUERY_GPS = QUERY_GPS_DEER
        elif dbname in ("euroboar_db"):
            QUERY_GPS = QUERY_GPS_BOAR
        else:
            print(f"Database {dbname} not recognized for GPS query.")
            return False
    # Execute the query and fetch the data safely
    with conn.cursor() as cursor:
        cursor.execute(QUERY_GPS)
        rows = cursor.fetchall()

        # Extract column names from the cursor description
        columns = [col[0] for col in cursor.description]

    # Create the Pandas DataFrame and close the connection
    gps_periods = pd.DataFrame(rows, columns=columns)
    conn.close()

    # Convert to datetime
    gps_periods["gps_min_start_time"] = pd.to_datetime(
        gps_periods["gps_min_start_time"]
    )
    gps_periods["gps_max_end_time"] = pd.to_datetime(gps_periods["gps_max_end_time"])

    # Filter out NA rows
    gps_periods = gps_periods.dropna(subset=["gps_min_start_time", "gps_max_end_time"])

    # Create the label: study_name (n = n_animals)
    gps_periods["study_label"] = (
        np.where(
            gps_periods["short_name"] != "",
            gps_periods["short_name"],
            gps_periods["study_name"],
        )
        + " (n = "
        + gps_periods["n_animals"].astype(str)
        + ")"
    )

    # Order the dataframe by gps_min_start_time so it plots properly
    # (ascending=False ensures the earliest date is at the top of the
    # y-axis in matplotlib)
    gps_periods = gps_periods.sort_values(by="gps_min_start_time", ascending=False)

    # Plotting ---
    fig, ax = plt.subplots(figsize=(12, 8))

    ax.hlines(
        y=gps_periods["study_label"],
        xmin=gps_periods["gps_min_start_time"],
        xmax=gps_periods["gps_max_end_time"],
        linewidth=2,
        color="blue",
    )

    ax.plot(
        gps_periods["gps_min_start_time"],
        gps_periods["study_label"],
        "o",
        color="blue",
        markersize=5,
    )

    ax.plot(
        gps_periods["gps_max_end_time"],
        gps_periods["study_label"],
        "o",
        color="blue",
        markersize=5,
    )

    if research_group:
        title = "GPS Data Availability Periods by Research Group"
        figtext = "Each bar represents the period between the first GPS start time and the last GPS end time for each research group"
        ax.set_ylabel("Research group")
    else:
        title = "GPS Data Availability Periods by Study Area"
        figtext = "Each bar represents the period between the first GPS start time and the last GPS end time for each study area"
        ax.set_ylabel("Study area")
    ax.set_title(title, fontweight="bold", pad=15)
    ax.set_xlabel("GPS data period")

    fig.text(
        0.5,
        0.01,
        figtext,
        ha="center",
        fontsize=9,
        color="dimgray",
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="x", linestyle="-", alpha=0.3)
    ax.tick_params(axis="y", labelsize=9, length=0)

    plt.tight_layout(rect=[0, 0.03, 1, 1])
    if output is None:
        iobytes = io.BytesIO()
        plt.savefig(iobytes, format="jpg", dpi=300)
        iobytes.seek(0)
        jsdata = base64.b64encode(iobytes.read()).decode()
        return jsdata
    else:
        plt.savefig(output, dpi=300)
    return True


def metadata_per_group(
    dbname,
    kingdom="Animalia",
    phylum="Chordata",
    order_name="Artiodactyla",
    family="Cervidae",
    species="Cervus elaphus",
    common_name="Roe Deer",
    study_area_id=None,
):
    """Function to create the plot of distribution of deployments per year

    Parameters:
        dbname (str): name of the database to connect to
        kingdom (str): Taxonomic kingdom
        phylum (str): Taxonomic phylum
        order_name (str): Taxonomic order
        family (str): Taxonomic family
        species (str): Taxonomic species
        common_name (str): Common name of the species

    Returns:
        list: a list with the value to show and the challenge
    """

    # Establish the psycopg2 connection
    if study_area_id:
        QUERY = QUERY_METADATA_ID.format(
            KINGDOM=kingdom,
            PHYLUM=phylum,
            ORDER=order_name,
            FAMILY=family,
            SPECIE=species,
            NAME=common_name,
            AREA_ID=study_area_id,
        )
    else:
        QUERY = QUERY_METADATA.format(
            KINGDOM=kingdom,
            PHYLUM=phylum,
            ORDER=order_name,
            FAMILY=family,
            SPECIE=species,
            NAME=common_name,
        )
    conn = _get_psycopg2_connection(dbname)
    with conn.cursor() as cursor:
        cursor.execute(QUERY)
        rows = cursor.fetchall()

        # Extract column names from the cursor description
        columns = [col[0] for col in cursor.description]

    # Create the Pandas DataFrame and close the connection
    meta = pd.DataFrame(rows, columns=columns)
    conn.close()
    return meta.to_json(orient="records", date_format="iso")


def _add_individual_name(parent, given_name, sur_name):
    """Helper to add an individualName element"""
    name_el = ET.SubElement(parent, "individualName")
    ET.SubElement(name_el, "givenName").text = str(given_name) if given_name else ""
    ET.SubElement(name_el, "surName").text = str(sur_name) if sur_name else ""
    return name_el


def _add_address(parent, country):
    """Helper to add an address element"""
    if not country:
        return None
    addr = ET.SubElement(parent, "address")
    ET.SubElement(addr, "country").text = str(country)
    return addr


def metadata_to_eml(
    metadata_data,
):
    """Convert the output of metadata_per_group to an EML 2.1.1 XML string.

    Parameters:
        metadata_data: JSON string or list of dicts (output of metadata_per_group)

    Returns:
        str or list: EML XML string for a single record, or list of XML strings
            when the input contains multiple records
    """
    if isinstance(metadata_data, str):
        records = json.loads(metadata_data)
    else:
        records = metadata_data

    if not isinstance(records, list):
        records = [records]

    results = []
    for rec in records:
        eml = ET.Element("eml:eml")
        eml.set("xmlns:eml", "eml://ecoinformatics.org/eml-2.1.1")
        eml.set("xmlns:dc", "http://purl.org/dc/terms/")
        eml.set(
            "xmlns:xsi",
            "http://www.w3.org/2001/XMLSchema-instance",
        )
        eml.set(
            "xsi:schemaLocation",
            "eml://ecoinformatics.org/eml-2.1.1 "
            "http://rs.gbif.org/schema/eml-gbif-profile/1.0.2/eml.xsd",
        )
        eml.set("xml:lang", "eng")

        # --- dataset ---
        dataset = ET.SubElement(eml, "dataset")

        ET.SubElement(dataset, "title").text = str(rec.get("title", ""))

        # --- creator ---
        creator = ET.SubElement(dataset, "creator")
        _add_individual_name(creator, rec.get("givenname1"), rec.get("surname1"))
        if rec.get("organizationname1"):
            ET.SubElement(creator, "organizationname").text = str(
                rec["organizationname1"]
            )
        if rec.get("positionname1"):
            ET.SubElement(creator, "positionname").text = str(rec["positionname1"])
        _add_address(creator, rec.get("country1"))
        if rec.get("electronicmailaddress1"):
            ET.SubElement(creator, "electronicMailAddress").text = str(
                rec["electronicmailaddress1"]
            )
        if rec.get("onlineUrl1"):
            ET.SubElement(creator, "onlineUrl").text = str(rec["onlineUrl1"])

        # --- metadataProvider ---
        metadata_provider = ET.SubElement(dataset, "metadataProvider")
        mp_name = ET.SubElement(metadata_provider, "individualName")
        ET.SubElement(mp_name, "givenName").text = str(
            rec.get("metadataProvider_givenname", "EUROMAMMALS")
        )
        ET.SubElement(mp_name, "surName").text = str(
            rec.get("metadataProvider_surname", "EUROMAMMALS")
        )
        ET.SubElement(metadata_provider, "organizationName").text = str(
            rec.get("metadataProvider_organizationname", "EUROMAMMALS")
        )
        if rec.get("metadataProvider_electronicMailAddress"):
            ET.SubElement(metadata_provider, "electronicMailAddress").text = str(
                rec["metadataProvider_electronicMailAddress"]
            )

        # --- associatedParty ---
        if rec.get("givenname2"):
            party = ET.SubElement(dataset, "associatedParty")
            _add_individual_name(party, rec.get("givenname2"), rec.get("surname2"))
            if rec.get("organizationname2"):
                ET.SubElement(party, "organizationName").text = str(
                    rec["organizationname2"]
                )
            if rec.get("positionname2"):
                ET.SubElement(party, "positionname").text = str(rec["positionname2"])
            _add_address(party, rec.get("country2"))
            if rec.get("electronicmailaddress2"):
                ET.SubElement(party, "electronicMailAddress").text = str(
                    rec["electronicmailaddress2"]
                )
            ET.SubElement(party, "role").text = "author"

        # --- pubDate ---
        ET.SubElement(dataset, "pubDate").text = date.today().isoformat()

        # --- language ---
        ET.SubElement(dataset, "language").text = "eng"

        # --- abstract ---
        abstract = ET.SubElement(dataset, "abstract")
        ET.SubElement(abstract, "para").text = (
            f"GPS data collection for movement ecology studies. "
            f"This dataset contains GPS telemetry data from "
            f"{rec.get('count_animals', 'N/A')} animals."
        )

        # --- keywordSet ---
        keyword_set = ET.SubElement(dataset, "keywordSet")
        if rec.get("keyword"):
            ET.SubElement(keyword_set, "keyword").text = str(rec["keyword"])
        ET.SubElement(keyword_set, "keyword").text = "Metadata"
        ET.SubElement(keyword_set, "keywordThesaurus").text = (
            "GBIF Dataset Type Vocabulary: "
            "http://rs.gbif.org/vocabulary/gbif/dataset_type.xml"
        )

        # --- intellectualRights ---
        rights = ET.SubElement(dataset, "intellectualRights")
        ET.SubElement(rights, "para").text = str(
            rec.get(
                "intellectualrights",
            )
        )

        # --- coverage ---
        coverage = ET.SubElement(dataset, "coverage")

        # geographicCoverage
        geo_cov = ET.SubElement(coverage, "geographicCoverage")
        ET.SubElement(geo_cov, "geographicDescription").text = (
            f"Bounding box for {rec.get('title', 'study area')}"
        )
        bounding = ET.SubElement(geo_cov, "boundingCoordinates")
        ET.SubElement(bounding, "westBoundingCoordinate").text = str(
            rec.get("min_x", "")
        )
        ET.SubElement(bounding, "eastBoundingCoordinate").text = str(
            rec.get("max_x", "")
        )
        ET.SubElement(bounding, "northBoundingCoordinate").text = str(
            rec.get("max_y", "")
        )
        ET.SubElement(bounding, "southBoundingCoordinate").text = str(
            rec.get("min_y", "")
        )

        # temporalCoverage
        if rec.get("begindate") and rec.get("enddate"):
            temp_cov = ET.SubElement(coverage, "temporalCoverage")
            range_dates = ET.SubElement(temp_cov, "rangeOfDates")
            begin = ET.SubElement(range_dates, "beginDate")
            ET.SubElement(begin, "calendarDate").text = str(rec["begindate"])[:10]
            end = ET.SubElement(range_dates, "endDate")
            ET.SubElement(end, "calendarDate").text = str(rec["enddate"])[:10]

        # taxonomicCoverage
        tax_cov = ET.SubElement(coverage, "taxonomicCoverage")
        ET.SubElement(tax_cov, "generalTaxonomicCoverage").text = str(
            rec.get("generalTaxonomicCoverage", "European terrestrial mammals")
        )
        for rank_name, rank_value in [
            ("kingdom", rec.get("kingdom")),
            ("phylum", rec.get("phylum")),
            ("order", rec.get("order_")),
            ("family", rec.get("family_")),
            ("species", rec.get("species")),
        ]:
            tc = ET.SubElement(tax_cov, "taxonomicClassification")
            ET.SubElement(tc, "taxonRankName").text = rank_name
            ET.SubElement(tc, "taxonRankValue").text = rank_value
        # add commonname to species level
        last_tc = tax_cov.findall("taxonomicClassification")[-1]
        ET.SubElement(last_tc, "commonname").text = rec.get("commonname")

        # --- contact ---
        contact = ET.SubElement(dataset, "contact")
        _add_individual_name(contact, rec.get("givenname1"), rec.get("surname1"))
        if rec.get("organizationname1"):
            ET.SubElement(contact, "organizationname").text = str(
                rec["organizationname1"]
            )
        _add_address(contact, rec.get("country1"))
        if rec.get("electronicmailaddress1"):
            ET.SubElement(contact, "electronicMailAddress").text = str(
                rec["electronicmailaddress1"]
            )

        # --- method ---
        methods_el = ET.SubElement(dataset, "methods")
        methodStep = ET.SubElement(methods_el, "methodStep")
        methodDesc = ET.SubElement(methodStep, "description")
        ET.SubElement(methodDesc, "para").text = rec.get("method")
        sampling_el = ET.SubElement(methods_el, "sampling")
        samplingExt = ET.SubElement(sampling_el, "studyExtent")
        samplingDesc = ET.SubElement(samplingExt, "description")
        ET.SubElement(samplingDesc, "para").text = "See Geographic Coverage"
        samplingDesc_el = ET.SubElement(sampling_el, "samplingDescription")
        ET.SubElement(samplingDesc_el, "para").text = rec.get("study_area_description")

        quality_el = ET.SubElement(methods_el, "qualityControl")
        qualityDesc = ET.SubElement(quality_el, "description")
        ET.SubElement(qualityDesc, "para").text = rec.get("qualitycontrol")

        # --- project ---
        project_el = ET.SubElement(dataset, "project")
        ET.SubElement(project_el, "title").text = str(rec.get("title", ""))
        personnel = ET.SubElement(project_el, "personnel")
        _add_individual_name(personnel, rec.get("givenname1"), rec.get("surname1"))
        ET.SubElement(personnel, "role").text = "principalInvestigator"

        # Serialize
        ET.indent(eml, space="  ")
        xml_str = ET.tostring(eml, encoding="unicode", xml_declaration=False)
        results.append(xml_str)

    if len(results) == 1:
        return results[0]
    return results
