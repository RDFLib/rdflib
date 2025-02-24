# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 18:21:28 2024

See issue https://github.com/RDFLib/rdflib/issues/2957.

@author: Administrator
"""
from rdflib import Graph, Literal, URIRef, Variable
import os

current_dir = os.getcwd()

GraphString = '''

prefix ex:  <https://www.example.org/>

ex:document ex:subject "Nice cars" .

ex:document ex:theme "Car" .

'''

someGraph = Graph()

someGraph.parse(data=GraphString , format="turtle")

# This query states first a normal triple pattern and then an optional clause with a subselect query.    
Query1 = someGraph.query('''
       
prefix ex:  <https://www.example.org/> 

select ?subject ?theme

where  {
    
    ?doc1 ex:subject ?subject.
 
    OPTIONAL
     {
       select ?theme
       where {
              ?doc1 ex:theme ?theme.       
       }
      }
    }
''')

filepath = current_dir+"/output1.txt"

# Print the results with variable names and their bindings
print ('\nResults for Query1: \n')
for row in Query1:
        print ("Result 'subject: "+ str(row.subject) + "'\nResult should show 'subject: Nice cars' \n")
        print ("Result 'theme: " + str(row.theme) + "'\nResult should show 'theme: Car'")
       
        with open(filepath, 'w', encoding='utf-8') as file:
           file.write(str(row))
# Result should yield two rows:
#   subject: Nice cars
#   theme: Car


# This query states first an optional clause with a subselect query and then a normal triple pattern.
Query2 = someGraph.query('''
       
prefix ex:  <https://www.example.org/> 

select ?subject ?theme

where  {
     
    OPTIONAL
     {
       select ?theme
       where {
              ?doc1 ex:theme ?theme.       
       }
      }
     ?doc1 ex:subject ?subject.
    }
''')

filepath = current_dir+"/output2.txt"

# Print the results with variable names and their bindings
print ('\nResults for Query2: \n')
for row in Query2:
        print ("Result 'subject: "+ str(row.subject) + "'\nResult should show 'subject: Nice cars' \n")
        print ("Result 'theme: " + str(row.theme) + "'\nResult should show 'theme: Car'")
       
        with open(filepath, 'w', encoding='utf-8') as file:
           file.write(str(row))

# Result should yield two rows:
#   subject: Nice cars
#   theme: Car           