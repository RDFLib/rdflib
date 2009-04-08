from rdflib import BNode
from rdflib.store import Store
from rdflib.Literal import Literal
import sys, re, os
from rdflib.term_utils import *
from rdflib.Graph import QuotedGraph
from rdflib.store.MySQL import SQL, MySQL, PostgreSQL
from rdflib.store import Store
from rdflib.store.FOPLRelationalModel.QuadSlot import *

from Ft.Lib import Uri
Any = None    

VALUES_EXPR     = re.compile('.*VALUES (\(.*\))')
TABLE_NAME_EXPR = re.compile('INSERT INTO (\S*)\s+VALUES')

ROW_DELIMITER = '\n'
COL_DELIMITER = '|'

DENORMALIZED_INDEX_TARGETS = [
  'subject', 'subject_term', 'predicate', 'predicate_term',
  'object', 'object_term', 'context', 'context_term']

def make_delimited(_list):
  return COL_DELIMITER.join(
    [i is None and 'NULL' or '"%s"' % i for i in _list])

class LoadError(Exception):
  pass

class DllError(Exception):
  pass

class DllNode(object):
  def __init__(self, stuff):
    self.prev = None
    self.next = None
    self.stuff = stuff

  def insert_before(self, following):
    prev = following.prev

    if prev is not None:
      prev.next = self

    self.prev = prev
    self.next = following

    following.prev = self

  def insert_after(self, preceding):
    next = preceding.next

    if next is not None:
      next.prev = self

    self.prev = preceding
    self.next = next

    preceding.next = self

  def remove(self):
    if self.prev is not None:
      self.prev.next = self.next
    if self.next is not None:
      self.next.prev = self.prev
    self.prev = None
    self.next = None

class RecentSet(object):
  def __init__(self, size):
    self.size = size
    self.store = {} 
    '''map from objects to their node in the doubly-linked list'''
    self.head = None
    '''first item in the doubly-linked list'''
    self.tail = None
    '''last item in the doubly-linked list'''

  def check(self, item):
    if item in self.store:
      node = self.store[item]
      if self.head is not node:
        if self.tail is node:
          self.tail = self.tail.prev
        node.remove()
        node.insert_before(self.head)
        self.head = node

      return True

    else:
      node = DllNode(item)

      if self.head is None:
        assert self.tail is None
        self.head = node
        self.tail = node
      else:
        node.insert_before(self.head)
        self.head = node

      self.store[item] = node

      if len(self.store) > self.size:
        drop = self.tail
        #print >> sys.stderr, "Dropping", drop.stuff
        self.tail = drop.prev
        drop.remove()
        del self.store[drop.stuff]

      return False

class Loader(SQL):

    # Thought: just have one table corresponding to each ending table (for
    # both tables below)
    TRIPLES_SQL_TEMPLATE = '''
      create table triples (
        subject bigint unsigned,
        subject_term enum('U','B','F','V'),
        predicate bigint unsigned,
        predicate_term enum('U','V'),
        object bigint unsigned,
        object_term enum('U','B','F','V','L'),
        data_type bigint unsigned default NULL,
        language varchar(3) default NULL,
        context bigint unsigned,
        context_term enum('U','B','F')
      )'''

    LEXICAL_SQL_TEMPLATE = '''
      create table lexical (
        id bigint unsigned,
        term_type enum('U','B','F','V','L'),
        lexical text
      )'''

    loadStatement = """LOAD DATA LOCAL INFILE '%s' IGNORE INTO TABLE
                       %s FIELDS TERMINATED BY '|' ENCLOSED BY '"'
                       ESCAPED BY '\\\\'"""

    def __init__(self, #triplesFileName=None, lexicalFileName=None,
                 delimited_directory='delimited_dumps',
                 reuseExistingFiles=False):
      mode = 'a'
      if not reuseExistingFiles:
        mode = 'w'
        try:
          os.mkdir(delimited_directory)
        except OSError:
          raise LoadError('Can\'t create `' + delimited_directory +
                          '\': it already exists.')

      self.delimited_directory = delimited_directory
        
      for table in self.tables:
        table.delimited_file = file(self.delimited_filename(table), mode)

      self.recent = RecentSet(100000)
      self.recent_hits = 0
      self.recent_misses = 0

    def delimited_filename(self, table, extension='.csv'):
      return os.path.join(self.delimited_directory,
                          table.get_name() + extension)

    def open(self, configuration=None, create=False):
      if configuration:
        super(Loader, self).open(configuration, create)

    def add(self, (subject, predicate, obj), context=None, quoted=False):
        self.addN([(subject, predicate, obj, context)])

    def addN(self, quads):
        for s,p,o,c in quads:
            assert c is not None, \
              "Context associated with %s %s %s is None!" % (s, p, o)
            qSlots = genQuadSlots([s, p, o, c.identifier],
                                  self.useSignedInts)

            table = self.get_table((s, p, o))
            table.delimited_file.write(make_delimited(
              table.makeRowComponents(qSlots)) + ROW_DELIMITER)

            for row in table.listIdentifiers(qSlots):
              if not self.recent.check((row[2], row[1])):
                self.idHash.delimited_file.write(make_delimited(
                  row) + ROW_DELIMITER)
                self.recent_misses += 1
              else:
                self.recent_hits += 1

            for row in table.listLiterals(qSlots):
              self.valueHash.delimited_file.write(make_delimited(
                row) + ROW_DELIMITER)

            if False:
                #print 'Writing data...', qSlots
                # Add to the denormalized delimited file: 
                beginning = True
                for item in qSlots:
                    parts = [item.md5Int, item.termType]
                    self.lexicalFile.write(make_delimited(
                      parts + [item.normalizeTerm()]) + ROW_DELIMITER)
                    if item.position == OBJECT:
                      dqs = item.getDatatypeQuadSlot()
                      if dqs is not None:
                        parts.append(dqs.md5Int)
                        self.lexicalFile.write(make_delimited(
                          [dqs.md5Int, 'U', dqs.normalizeTerm()]) +
                          ROW_DELIMITER)
                      else:
                        parts.append(None)

                      if item.termType == 'L':
                        parts.append(item.term.language)
                      else:
                        parts.append(None)
                    if not beginning:
                        self.triplesFile.write(COL_DELIMITER)
                    beginning = False    
                    self.triplesFile.write(make_delimited(parts))
                self.triplesFile.write(ROW_DELIMITER)

    def dumpRDF(self, suffix):
      for table in self.tables:
        table.delimited_file.close()
      print >> sys.stderr, 'Recent hits:', self.recent_hits
      print >> sys.stderr, 'Recent misses:', self.recent_misses

    def makeLoadStatement(self, fileName, tableName):
      return self.loadStatement % (fileName, tableName)

    def initDenormalizedTables(self, cursor):
      raise NotImplementedError(
        'This method has been deprecated.  See `load_temporary_tables` instead.')

    def load_temporary_tables(self, cursor):
      if self.triplesFileName is None or self.lexicalFileName is None:
        return

      if self.triplesFile and not self.triplesFile.closed:
        self.triplesFile.close()

      cursor.execute(self.TRIPLES_SQL_TEMPLATE)
      cursor.execute(self.makeLoadStatement(self.triplesFileName, 'triples'))

      if self.lexicalFile and not self.lexicalFile.closed:
        self.lexicalFile.close()

      cursor.execute(self.LEXICAL_SQL_TEMPLATE)
      cursor.execute(self.makeLoadStatement(self.lexicalFileName, 'lexical'))

    def indexTriplesTable(self, cursor, columns=[]):
      for column in columns:
        cursor.execute('CREATE INDEX triples_%s ON triples (%s)' %
                       ((column,) * 2))
      cursor.execute('CREATE INDEX triples_all ON triples (%s)' %
                     (', '.join(columns),))

    def indexLexicalTable(self, cursor):
      cursor.execute('CREATE INDEX lexical_id ON lexical (id)')
      cursor.execute('CREATE INDEX lexical_term_type ON lexical (term_type)')

    def loadAssociativeBox(self, indexFirst=False):
      cursor = self._db.cursor()
      cursor.execute("""
        insert into %s
        select distinct subject as member, subject_term as member_term,
                        object as class, object_term as class_term,
                        context, context_term
        from triples where predicate = %s and predicate_term = 'U'""" %
          (self.aboxAssertions,
           str(normalizeNode(RDF.type, self.useSignedInts))))

    def loadLiteralProperties(self, indexFirst=False):
      cursor = self._db.cursor()
      cursor.execute("""
        insert into %s
        select distinct subject, subject_term, predicate, predicate_term,
                        object, context, context_term, data_type, language
        from triples where object_term = 'L'
      """ %
          (self.literalProperties,))

    def loadRelations(self, indexFirst=False):
      cursor = self._db.cursor()
      cursor.execute("""
        insert into %s
        select distinct subject, subject_term, predicate, predicate_term,
                        object, object_term, context, context_term
        from triples where predicate != %s and object_term != 'L'""" %
          (self.binaryRelations,
           str(normalizeNode(RDF.type, self.useSignedInts))))

    def loadLiterals(self, indexFirst=False):
      cursor = self._db.cursor()
      cursor.execute("""
        insert into %s select distinct id, lexical from lexical where
        term_type = 'L'""" % (self.valueHash,))

    def loadIdentifiers(self, indexFirst=False):
      cursor = self._db.cursor()
      cursor.execute("""
        insert into %s select distinct id, term_type,
        lexical from lexical where
        term_type != 'L'""" % (self.idHash,))

    def remove(self, triple_pattern, context):
        pass

    #Transactional interfaces
    def commit(self):
        """ """
        pass
    
    def rollback(self):
        """ """
        pass

    def bind(self, prefix, namespace):
        """ """
        pass
    
    def prefix(self, namespace):
        """ """
        pass
    
    def namespace(self, prefix):
        """ """
        pass
    
    def namespaces(self):
        pass

class MySQLLoader(Loader, MySQL):
    def __init__(self, identifier=None, configuration=None,
                 delimited_directory='delimited_dumps',
                 reuseExistingFiles=False):
        MySQL.__init__(self, identifier, configuration, debug=True,
                       engine="ENGINE=MyISAM")
        Loader.__init__(self, delimited_directory, reuseExistingFiles)

    def delimited_filename(self, table):
      return Loader.delimited_filename(self, table, '.csv.mysql')

    def _loadTable(self, table, indexFirst=False):
      cursor = self._db.cursor()

      sql = 'ALTER TABLE %s DISABLE KEYS' % (table.get_name(),)
      self.log_statement(sql)
      cursor.execute(sql)

      sql = self.makeLoadStatement(
        self.delimited_filename(table), table.get_name())
      self.log_statement(sql)
      cursor.execute(sql)

      sql = 'ALTER TABLE %s ENABLE KEYS' % (table.get_name(),)
      self.log_statement(sql)
      cursor.execute(sql)

    def loadAssociativeBox(self, indexFirst=False):
      self._loadTable(self.aboxAssertions)
      return

      cursor = self._db.cursor()
      sql = """
        insert into %s
        select subject as member, subject_term as member_term,
               object as class, object_term as class_term,
               context, context_term
        from triples
        where predicate = %s and predicate_term = 'U'
        group by subject, object, context
      """ % (self.aboxAssertions,
             str(normalizeNode(RDF.type, self.useSignedInts)))
      print >> sys.stderr, sql
      cursor.execute(sql)

    def loadLiteralProperties(self, indexFirst=False):
      self._loadTable(self.literalProperties)
      return

      cursor = self._db.cursor()
      sql = """
        insert into %s
        select subject, subject_term, predicate, predicate_term,
               object, context, context_term, data_type, language
        from triples
        where object_term = 'L'
        group by subject, predicate, object, context
      """ % (self.literalProperties,)
      print >> sys.stderr, sql
      cursor.execute(sql)

    def loadRelations(self, indexFirst=False):
      self._loadTable(self.binaryRelations)
      return

      cursor = self._db.cursor()
      sql = """
        insert into %s
        select subject, subject_term, predicate, predicate_term,
               object, object_term, context, context_term
        from triples
        where predicate != %s and object_term != 'L'
        group by subject, predicate, object, context
      """ % (self.binaryRelations,
             str(normalizeNode(RDF.type, self.useSignedInts)))
      print >> sys.stderr, sql
      cursor.execute(sql)

    def loadLiterals(self, indexFirst=False):
      self._loadTable(self.valueHash)
      return

      cursor = self._db.cursor()
      sql = """
        insert into %s select id, lexical from lexical 
        where term_type = 'L' group by id
      """ % (self.valueHash,)
      print >> sys.stderr, sql
      cursor.execute(sql)

    def loadIdentifiers(self, indexFirst=False):
      self._loadTable(self.idHash)
      return

      cursor = self._db.cursor()
      sql = """
        insert into %s select id, term_type, lexical from lexical 
        where term_type != 'L' group by id
      """ % (self.idHash,)
      print >> sys.stderr, sql
      cursor.execute(sql)

class PostgreSQLLoader(Loader, PostgreSQL):

    TRIPLES_SQL_TEMPLATE = '''
      create table denormalized (
        subject bigint,
        subject_term char,
        predicate bigint,
        predicate_term char,
        object bigint,
        object_term char,
        data_type bigint default NULL,
        language varchar(3) default NULL,
        context bigint,
        context_term char
      )'''

    LEXICAL_SQL_TEMPLATE = '''
      create table lexical (
        id bigint,
        term_type char,
        lexical text
      )'''

    loadStatement = """COPY %s FROM '%s' WITH DELIMITER '|'
                       NULL AS 'NULL' CSV ESCAPE E'\\\\'"""

    def __init__(self, identifier=None, configuration=None,
                 delimited_directory='delimited_dumps',
                 reuseExistingFiles=False):
        PostgreSQL.__init__(self, identifier, configuration, debug=True)
        Loader.__init__(self, delimited_directory, reuseExistingFiles)

    def delimited_filename(self, table):
      return Loader.delimited_filename(self, table, '.csv.postgresql')

    def makeLoadStatement(fileName, tableName):
      return self.loadStatement % (tableName, fileName)

def timing(config, tableid, dumpfile):
  plugins = ['MySQL', 'PostgreSQL']
  index = 0
  runs = {}
  for plugin in plugins:
    if options.delete:
      store = rdflib.plugin.get(plugin, Store)(tableid)
      store.open(config)
      cursor = store._db.cursor()
      #cursor.execute('DROP TABLE denormalized')
      store.destroy(config)
      store.close()

    start = datetime.datetime.now()
    print start
    store = rdflib.plugin.get(plugin, Store)(tableid)

    runid = 'run' + str(index)
    runs[runid] = [plugin, 'no denormalized indices',
                   'index store before load']
    store.create(config, False)
    store.applyIndices()
    store.applyForeignKeys()

    cursor = store._db.cursor()

    hashFieldType = store.hashFieldType
    load_temporary_tables(cursor)

    loadLiterals(store)
    loadIdentifiers(store)
    loadAssociativeBox(store)
    loadLiteralProperties(store)
    loadRelations(store)

    stop = datetime.datetime.now()
    print stop
    runs[runid].append(str(stop - start))
    print '\t'.join(runs[runid])

    cursor.execute('DROP TABLE triples')
    cursor.execute('DROP TABLE lexical')
    store.destroy(config)
    index = index + 1

    #start = time.clock()
    start = datetime.datetime.now()
    store = rdflib.plugin.get(plugin, Store)(tableid)

    runid = 'run' + str(index)
    runs[runid] = [plugin, 'no denormalized indices',
                   'index store after load']
    store.create(config, False)

    cursor = store._db.cursor()

    hashFieldType = store.hashFieldType
    load_temporary_tables(cursor)

    loadLiterals(store)
    loadIdentifiers(store)
    loadAssociativeBox(store)
    loadLiteralProperties(store)
    loadRelations(store)

    store.applyIndices()
    store.applyForeignKeys()

    stop = datetime.datetime.now()
    runs[runid].append(str(stop - start))
    print '\t'.join(runs[runid])

    cursor.execute('DROP TABLE triples')
    cursor.execute('DROP TABLE lexical')
    store.destroy(config)
    index = index + 1

PLUGIN_MAP = {
    'MySQL': MySQLLoader,
    'PostgreSQL': PostgreSQLLoader,
  }

def main():
  from optparse import OptionParser
  usage = '''usage: %prog [options] <DB Type>'''
  op = OptionParser(usage=usage)
  op.add_option('-c', '--connection', help='Database connection string')
  op.add_option('-i', '--id', help='Database table set identifier')
  op.add_option('--triples',
    help = 'Name of SQL dump file for triples')
  op.add_option('--lexical',
    help = 'Name of SQL dump file for lexical values')
  op.add_option('-r', '--reuse', action='store_true',
    help = 'Reuse existing denormalized files instead of creating new ones')

  op.add_option('-d', '--delete', action='store_true',
    help = 'Delete old repository before starting')

  op.add_option('--name', dest='graphName',
    help = 'The name of the graph to parse the RDF serialization(s) into')

  op.add_option('-x', '--xml', action='append',
    help = 'Append to the list of RDF/XML documents to parse')
  op.add_option('-t', '--trix', action='append',
    help = 'Append to the list of TriX documents to parse')
  op.add_option('-n', '--n3', action='append',
    help = 'Append to the list of N3 documents to parse')
  op.add_option('--nt', action='append',
    help = 'Append to the list of NT documents to parse')
  op.add_option('-a', '--rdfa', action='append',
    help = 'Append to the list of RDFa documents to parse')

  op.add_option('--directory',
    help = 'Load all children of this directory into the repository')
  op.add_option('--format', type='choice',
    choices = ['xml', 'n3', 'nt', 'rdfa', 'trix'],
    help = 'Format of files found when using `--directory`')

  op.add_option('--catalog',
    help = 'Catalog to use to resolve local URIs to identify graphs')

  op.add_option('--timing', action='store_true',
    help = 'Run timing tests')

  op.set_defaults(connection=None, reuse=False, id=None,
                  xml=[], trix=[], n3=[], nt=[], rdfa=[],
                  graphName=BNode())
  (options, args) = op.parse_args()

  if options.triples is not None:
    options.triples = os.path.abspath(options.triples)
  if options.lexical is not None:
    options.lexical = os.path.abspath(options.lexical)

  try:
    store = PLUGIN_MAP[args[0]](identifier=options.id,
      triplesFileName=options.triples, lexicalFileName=options.lexical,
      reuseExistingFiles=options.reuse)
  except Exception:
    op.error('You need to provide a database type (MySQL or PostgreSQL).')

  store.open(options.connection)
  
  factGraph = ConjunctiveGraph(store, identifier=options.graphName)
  if not options.reuse:
    if options.directory:
      if not options.format:
        op.error('You need to provide the format with `--format`\n' +
                 'when loading from a directory')
      dirparts = os.walk(options.directory).next()
      for entry in dirparts[2]:
        graphRef = os.path.join(dirparts[0], entry)
        factGraph.parse(graphRef, publicID=Uri.OsPathToUri(graphRef),
                        format = options.format)

    for graphRef in options.xml:
      factGraph.parse(graphRef, publicID=Uri.OsPathToUri(graphRef),
                      format='xml')
    for graphRef in options.trix:
      factGraph.parse(graphRef, publicID=Uri.OsPathToUri(graphRef),
                      format='trix')
    for graphRef in options.n3:
      factGraph.parse(graphRef, publicID=Uri.OsPathToUri(graphRef),
                      format='n3')
    for graphRef in options.nt:
      factGraph.parse(graphRef, publicID=Uri.OsPathToUri(graphRef),
                      format='nt')
    for graphRef in options.rdfa:
      factGraph.parse(graphRef, publicID=Uri.OsPathToUri(graphRef),
                      format='rdfa')
    store.dumpRDF('solo')
  store.close()

  if options.connection:
    if not options.id:
      op.error('You need to provide a table set identifier')

    if options.timing:
      timing(config, tableid, dumpfile)
    else:
      if options.delete:
        store.open(options.connection)
        cursor = store._db.cursor()
        cursor.execute('DROP TABLE triples')
        cursor.execute('DROP TABLE lexical')
        store.destroy(options.connection)
        store.close()

      #store = rdflib.plugin.get('MySQL', Store)(tableid)

      store.create(options.connection, False)
      store.applyIndices()
      store.applyForeignKeys()

      cursor = store._db.cursor()

      hashFieldType = store.hashFieldType
      store.load_temporary_tables(cursor)

      store.loadLiterals()
      store.loadIdentifiers()
      store.loadAssociativeBox()
      store.loadLiteralProperties()
      store.loadRelations()

      #cursor.execute('DROP TABLE denormalized')

if __name__ == '__main__':
  main()
