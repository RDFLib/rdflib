# -*- coding: utf-8 -*-
"""
Various utilities for pyMicrodata

@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
"""

"""
$Id: utils.py,v 1.9 2014-12-17 08:52:43 ivan Exp $
$Date: 2014-12-17 08:52:43 $
"""
import sys
import socket
from rdflib.namespace import XSD

# The separate W3C branch is necessary for the local security setup at W3C. It is ugly to have this
# in the code, but I was lazy to make it more generic...
# With the inclusion of pyMicrodata into RDFLib, this service looses its importance anyway...
if socket.getfqdn().endswith(".w3.org"):
    import checkremote

    url_opener = checkremote.safe_url_opener
else:
    import urllib.request

    url_opener = urllib.request.build_opener()
from urllib.request import Request
from urllib.parse import urljoin, quote, urlparse
from http.server import BaseHTTPRequestHandler
from urllib.error import HTTPError as urllib_HTTPError
from datetime import datetime


#################################################################################
def is_absolute_URI(uri):
    return urlparse(uri)[0] != ""


#################################################################################
def fragment_escape(name):
    return quote(name, "/~:-.")


#################################################################################
def generate_uri(base, v):
    """
    Generate an (absolute) URI; if val is a fragment, then using it with base,
    otherwise just return the value
    @param base: Absolute URI for base
    @param v: relative or absolute URI
    """
    if is_absolute_URI(v):
        return v


#################################################################################
def get_Literal(Pnode):
    """
    Get (recursively) the full text from a DOM Node.

    @param Pnode: DOM Node
    @return: string
    """
    rc = ""
    for node in Pnode.childNodes:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
        elif node.nodeType == node.ELEMENT_NODE:
            rc = rc + get_Literal(node)

    # This presupposes that all spaces and such should be stripped. I am not sure it is true in the spec,
    # but this is what the examples show
    # return re.sub(r'(\r| |\n|\t)+'," ",rc).strip()

    # at present, the agreement seems to say that white spaces are maintained:
    return rc


#################################################################################
def get_lang(node):
    # we may have lang and xml:lang
    retval = None
    if node.hasAttribute("lang"):
        retval = node.getAttribute("lang")
    if retval and node.hasAttribute("xml:lang"):
        xmllang = node.getAttribute("xml:lang").lower()
        if not (xmllang is not None and xmllang == retval.lower()):
            # This is an error, in which case retval must be invalidated...
            retval = None
    return retval


def get_lang_from_hierarchy(document, node):
    lang = get_lang(node)
    if lang is None:
        parent = node.parentNode
        if parent is not None and parent != document:
            return get_lang_from_hierarchy(document, parent)
        else:
            return get_lang(document)
    else:
        return lang


#################################################################################
datetime_type = XSD.dateTime
time_type = XSD.time
date_type = XSD.date
date_gYear = XSD.gYear
date_gYearMonth = XSD.gYearMonth
date_gMonthDay = XSD.gMonthDay
duration_type = XSD.duration

_formats = {
    date_gMonthDay: ["%m-%d"],
    date_gYearMonth: ["%Y-%m"],
    date_gYear: ["%Y"],
    date_type: ["%Y-%m-%d", "%Y-%m-%dZ"],
    time_type: ["%H:%M", "%H:%M:%S", "%H:%M:%SZ", "%H:%M:%S.%f"],
    datetime_type: [
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%MZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
    ],
    duration_type: [
        "P%dD",
        "P%YY%mM%dD",
        "P%YY%mM",
        "P%YY%dD",
        "P%YY",
        "P%mM",
        "P%mM%dD",
    ],
}

_dur_times = ["%HH%MM%SS", "%HH", "%MM", "%SS", "%HH%MM", "%HH%SS", "%MM%SS"]


def get_time_type(string):
    """
    Check whether the string abides to one of the accepted time related datatypes, and returns that one if yes
    @param string: the attribute value to be checked
    @return : a datatype URI or None
    """
    for key in _formats:
        for f in _formats[key]:
            try:
                # try to check if the syntax is fine
                d = datetime.strptime(string, f)
                # bingo!
                return key
            except ValueError:
                pass

    # Now come the special cases:-(
    # Check first for the duration stuff, that is the nastiest.
    if len(string) > 2 and string[0] == "P" or (string[0] == "-" and string[1] == "P"):
        # this is meant to be a duration type
        # first of all, get rid of the leading '-' and check again
        if string[0] == "-":
            for f in _formats[duration_type]:
                try:
                    # try to check if the syntax is fine
                    d = datetime.strptime(string, f)
                    # bingo!
                    return duration_type
                except ValueError:
                    pass
        # Let us see if the value contains a separate time portion, and cut that one
        durs = string.split("T")
        if len(durs) == 2:
            # yep, so we should check again
            dur = durs[0]
            tm = durs[1]
            # Check the duration part
            td = False
            for f in _formats[duration_type]:
                try:
                    # try to check if the syntax is fine
                    d = datetime.strptime(dur, f)
                    # bingo!
                    td = True
                    break
                except ValueError:
                    pass
            if td:
                # Getting there...
                for f in _dur_times:
                    try:
                        # try to check if the syntax is fine
                        d = datetime.strptime(tm, f)
                        # bingo!
                        return duration_type
                    except ValueError:
                        pass
            # something went wrong...
            return None
        else:
            # Well, no more tricks, this is a plain type
            return None

    # If we got here, we should check the time zone
    # there is a discrepancy between the python and the HTML5/XSD lexical string,
    # which means that this has to handled separately for the date and the timezone portion
    try:
        # The time-zone-less portion of the string
        s = string[0:-6]
        # The time-zone portion
        tz = string[-5:]
        try:
            t = datetime.strptime(tz, "%H:%M")
        except ValueError:
            # Bummer, this is not a correct time
            return None
        # The time-zone is fine, the datetime portion has to be checked
        for f in _formats[datetime_type]:
            try:
                # try to check if it is fine
                d = datetime.strptime(s, f)
                # Bingo!
                return datetime_type
            except ValueError:
                pass
    except:
        pass
    return None


#########################################################################################################
# Handling URIs
class URIOpener:
    """A wrapper around the urllib2 method to open a resource. Beyond accessing the data itself, the class
    sets the content location.
    The class also adds an accept header to the outgoing request, namely
    text/html and application/xhtml+xml (unless set explicitly by the caller).

    @ivar data: the real data, ie, a file-like object
    @ivar headers: the return headers as sent back by the server
    @ivar location: the real location of the data (ie, after possible redirection and content negotiation)
    """

    CONTENT_LOCATION = "Content-Location"

    def __init__(self, name):
        """
        @param name: URL to be opened
        @keyword additional_headers: additional HTTP request headers to be added to the call
        """
        try:
            # Note the removal of the fragment ID. This is necessary, per the HTTP spec
            req = Request(url=name.split("#")[0])
            req.add_header("Accept", "text/html, application/xhtml+xml")

            self.data = url_opener.open(req)
            self.headers = self.data.info()

            if URIOpener.CONTENT_LOCATION in self.headers:
                self.location = urlparse.urljoin(
                    self.data.geturl(), self.headers[URIOpener.CONTENT_LOCATION]
                )
            else:
                self.location = name

        except urllib_HTTPError:
            e = sys.exc_info()[1]
            from pyMicrodata import HTTPError

            msg = BaseHTTPRequestHandler.responses[e.code]
            raise HTTPError("%s" % msg[1], e.code)
        except Exception:
            e = sys.exc_info()[1]
            from pyMicrodata import MicrodataError

            raise MicrodataError("%s" % e)
