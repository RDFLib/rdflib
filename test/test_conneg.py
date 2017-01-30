import time


from rdflib import Graph

from six.moves import _thread
from six.moves.BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

"""
Test that correct content negoation headers are passed
by graph.parse
"""


xmltestdoc="""<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
   xmlns="http://example.org/"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
>
  <rdf:Description rdf:about="http://example.org/a">
    <b rdf:resource="http://example.org/c"/>
  </rdf:Description>
</rdf:RDF>
"""

n3testdoc="""@prefix : <http://example.org/> .

:a :b :c .
"""

nttestdoc="<http://example.org/a> <http://example.org/b> <http://example.org/c> .\n"


class TestHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        self.send_response(200, "OK")
        # fun fun fun parsing accept header.

        acs=self.headers["Accept"].split(",")
        acq=[x.split(";") for x in acs if ";" in x]
        acn=[(x,"q=1") for x in acs if ";" not in x]
        acs=[(x[0], float(x[1].strip()[2:])) for x in acq+acn]
        ac=sorted(acs, key=lambda x: x[1])
        ct=ac[-1]

        if "application/rdf+xml" in ct:
            rct="application/rdf+xml"
            content=xmltestdoc
        elif "text/n3" in ct:
            rct="text/n3"
            content=n3testdoc
        elif "text/plain" in ct:
            rct="text/plain"
            content=nttestdoc

        self.send_header("Content-type",rct)
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def log_message(self, *args):
        pass

def runHttpServer(server_class=HTTPServer,
        handler_class=TestHTTPHandler):
    """Start a server than can handle 3 requests :)"""
    server_address = ('localhost', 12345)
    httpd = server_class(server_address, handler_class)

    httpd.handle_request()
    httpd.handle_request()
    httpd.handle_request()


def testConNeg():
    _thread.start_new_thread(runHttpServer, tuple())
    # hang on a second while server starts
    time.sleep(1)
    graph=Graph()
    graph.parse("http://localhost:12345/foo", format="xml")
    graph.parse("http://localhost:12345/foo", format="n3")
    graph.parse("http://localhost:12345/foo", format="nt")


if __name__ == "__main__":

    import sys
    import nose
    if len(sys.argv)==1:
        nose.main(defaultTest=sys.argv[0])
