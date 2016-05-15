from rdflib import *

ex = Namespace('http://ex.co/')
g = Graph()
g.namespace_manager.bind('', ex)

g.add((ex.s1, ex.p, ex.o1))
g.add((ex.s1, ex.p, ex.o2))
g.add((ex.s1, ex.p, ex.o3))

g.add((ex.s2, ex.p, ex.o2))
g.add((ex.s2, ex.p, ex.o3))
g.add((ex.s2, ex.p, ex.o4))
g.add((ex.s2, ex.p, ex.o5))

g.add((ex.s3, ex.p, ex.o1))
g.add((ex.s3, ex.p, ex.o3))
g.add((ex.s3, ex.p, ex.o5))


print(g.serialize(format="n3"))

# should be
#    :s1 :p :o1, :o2, :o3 .
#    :s2 :p :o2, :o3, :o4, :o5 .
#    :s3 :p :o1, :o3, :o5 .

print '---'

print(g.query("""
PREFIX : <http://ex.co/>

SELECT ?o ?new
WHERE {
  :s1 :p ?o .
  :s2 :p ?o .
  OPTIONAL {
    :s3 :p ?o .
    BIND(:s4 as ?new)
  }
}
""").serialize(format="csv"))

# should be
#    :o2 ,
#    :o3 , :s4

print '---'

g.update("""
PREFIX : <http://ex.co/>

DELETE { :s1 :p ?o }
INSERT { ?new :p ?o }
WHERE {
  :s1 :p ?o .
  :s2 :p ?o .
  OPTIONAL {
    :s3 :p ?o .
    BIND(:s4 as ?new)
  }
}
""")

print(g.serialize(format="n3"))

# should now be
#    :s1 :p :o1 .
#    :s2 :p :o2, :o3, :o4, :o5 .
#    :s3 :p :o1, :o3, :o5 .
#    :s4 :p :o3 .
