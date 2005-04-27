#!/usr/local/bin/python2.4

"""
run.py is for loading and running python programs.

For help on run see:

   run.py --help
"""

import sys, logging, traceback

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s %(message)s')

__version__ = "2005/04/27"

logging.info("run.py version: %s" % __version__)


if __name__=="__main__":
    "Parse command line options if being run from the command line"
    from optparse import OptionParser
    usage = "usage: %prog [options] [<program_uri>] [args]"
    parser = OptionParser(usage=usage)
    # where to doc what program_uri "program url"    
    parser.allow_interspersed_args = False
    parser.add_option("--install-rdflib", dest="install_rdflib", action="store_true", help="download and install latest rdflib")
    parser.add_option("--update", action="store_true", dest="update", help="update program")    
    parser.add_option("--quiet", action="store_true", dest="quiet", help="")    
    parser.add_option("--backend", dest="backend", help="name of rdflib Graph backend to use")    
    parser.add_option("--path", dest="path", help="path to database")

    parser.set_defaults(path="__db__", version = None, update=False, quiet=False, backend=None, install_rdflib=False)

    (options, args) = parser.parse_args()
    if options.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    if options.install_rdflib:
        logging.info("downloading rdflib")
        import os
        from subprocess import Popen
        from tarfile import TarFile
        from urllib2 import urlopen, Request
        from StringIO import StringIO

        url = "http://rdflib.net/rdflib.tgz"
        headers = {'User-agent': 'run.py (http://rdflib.net/)' % __version__}
        f = urlopen(Request(url, None, headers))
        sio = StringIO(f.read())
        sio.seek(0)
        tar = TarFile.gzopen("rdflib.tgz", fileobj=sio)

        logging.info("extracting rdflib")
        for member in tar:
            if member.name.endswith("setup.py"):
                setup = member.name
            tar.extract(member)
        dir, file = os.path.split(setup)
        os.chdir(dir)

        logging.info("installing rdflib")
        p = Popen([sys.executable, "setup.py", "install"])
        p.wait()
        if "rdflib" in sys.modules:
            del sys.modules["rdflib"]
        try:
            import rdflib
            logging.info("rdflib %s installed" % rdflib.__version__)
        except ImportError, e:
            logging.info("rdflib not installed: %s" % e)    
        sys.exit()

def show_install_message(msg):
    logging.critical(msg)
    logging.critical("""Try the --install-rdflib option or""")
    logging.critical("""See http://rdflib.net/ for information on downloading and installing rdflib.""")
    sys.exit(-1)

try:
    import rdflib
except:
    show_install_message("rdflib not found")
else:
    version = tuple([int(x) for x in rdflib.__version__.split(".", 2)])    
    REQUIRED = (2, 1, 0)
    if version < REQUIRED:
        show_install_message("rdflib %s or greater required. Found rdflib version %s" % ("%s.%s.%s" % REQUIRED, rdflib.__version__))        

logging.info("rdflib version: %s" % rdflib.__version__)

from rdflib import RDF, RDFS, Graph, URIRef, BNode, Namespace

PYTHON = Namespace("http://rdflib.net/2005/python#")
PYTHON.Loader = PYTHON["Loader"]
PYTHON.program = PYTHON["program"]
PYTHON.code = PYTHON["code"]
PYTHON.LoaderDefaults = PYTHON["LoaderDefaults"]


class PythonLoader(Graph):

    def __init__(self, backend):
        backend = backend or "Sleepycat"
        super(PythonLoader, self).__init__(backend)
        self.__log = None        
        self.__config = None

    def __get_log(self):
        if self.__log is None:
            self.__log = logging
        return self.__log
    log = property(__get_log, doc="log facility")

    def __set_program(self, program):
        self.config.remove((PYTHON.Loader, PYTHON.program, None))
        if program:
            self.config.add((PYTHON.Loader, PYTHON.program, program))
    
    def __get_program(self):
        program = self.value(PYTHON.Loader, PYTHON.program)
        if not program:
            program = self.value(PYTHON.LoaderDefaults, PYTHON.program)
            assert program, "No default program found"            
            self.program = program
        return program
    program = property(__get_program, __set_program, doc="python program run.py will load and execute")
    
    def __get_config(self):
        config = self.__config
        if config is None:
           config =  self.__config = self.get_context(BNode("_config"))
        return config
    config = property(__get_config, doc="context for storing configuration data")

    def open(self, path):
        super(PythonLoader, self).open(path)

    def main(self, options, args):
        update = options.update
        try:
            self.open(options.path)
            if update or not (PYTHON, None, None) in self:
                self.program = None 
                self.log.info("loading: %s" % PYTHON)
                self.load(PYTHON)
            if len(args)>0:
                arg = args[0]
                if ":" in arg and "://" not in arg:
                    prefix, name = arg.split(":", 1)
                    if prefix=="":
                        program = PYTHON + arg[1:]
                    else:
                        namespace = dict(self.namespaces()).get(prefix, None)
                        if namespace is None:
                            self.log.warning("no known namespace for '%s'.")
                            namespace = PYTHON
                        program = namespace + name
                self.program = URIRef(self.absolutize(program, defrag=0))
                args = args[1:]
            program = self.program
            if update or not ((program, RDF.value, None) in self or (program, PYTHON.code, None) in self):
                self.log.info("loading: %s" % program)
                self.load(program)

            self.log.info("running: %s ( %s )" % (self.label(program, ''), program))

            code = self.value(program, PYTHON.code, default=program)
            if update or not (code, RDF.value, None) in self:
                self.log.info("loading: %s" % code)
                self.load(code)
            
            codestr = self.value(code, RDF.value)
            assert codestr, "No codestr found for: %s" % program
            try:
                c = compile(codestr+"\n", program, "exec")
                exec c in dict({"loader": self, "args": args})
            except Exception, e:
                self.log.error("\nWhile trying to exec %s the following exception occurred:\n" % program)
                self.log.error(traceback.print_exc())
        finally:
            self.close()

if __name__=="__main__":
    loader = PythonLoader(backend=options.backend)    
    loader.main(options, args)
