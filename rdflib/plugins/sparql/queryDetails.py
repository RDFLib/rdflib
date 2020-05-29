"""
This Module queryDetails.py is to find more details about the query and to compare two queries.
There are some functions as following
print_formalized_query(): This function is for printing formalized query which is used by the engin.
queryEquivalenceScore(q1,q2): This function is for finding similarity between two queries.

"""
" importing required modules "
from rdflib.plugins.sparql.parserutils import CompValue, Expr
import rdflib
import re
import numpy as np
from numpy import sqrt

" Testing whether module is working properly or not "
def testing():
    # print("Working properly")
    return "Working properly"

" This function is for formatting the query and printing part by part "
def get_formal_query(q, ind="    "):
    if not isinstance(q, CompValue):

        # print()
        # print(type(p))
        # print(p)

        if type(q) is list:
            for x in q:
                # print(x)
                if type(x) is tuple:
                    for y in x:
                        # print(type(y))
                        print("",end="")


                        # op_list.append(str(type(y))[8:-2]+"()")
        elif type(q) is set:
            for x in q.copy():
                print("", end="")
                # print(x)
                # p[p.index(x)]=' '
                # print(p[p.index(x)])
                # if type(x) is tuple:
                #     for y in x:
                #         print(type(y))
                # op_list.append(str(type(x))[8:-2]+"()")
                # op_list.append(str(x))
                # x='a'
                # st="a"
                # type(st)=type(x);
                # Class < > cls = Class.forName(className);
                # v=st;
                # p.add(v)
                # p.remove(x)
        print(q)
        return
    print("%s(" % (q.name,))
    for k in q:
        print("%s%s =" % (ind, k,), end=' ')
        get_formal_query(q[k], ind + "    ")
    print("%s)" % ind)

" finding algebra of query and provide it to formatted printing"
def printFormalizedQuery(q):
    print(" ###################### This is the final formalized Query ######################")
    try:

        get_formal_query(q.algebra)
    except AttributeError:
        # it's update, just a list
        for x in q:
            get_formal_query(x)
    print(" #################################################################")
    return
" finding the content of the query and return it to analyse"

def get_formal_query_content(p,op_list,ind="    "):
    if not isinstance(p, CompValue):

        # print(op_list)
        # print(type(p))
        # print(p)
        if type(p) is list:
            for x in p:
                # print(x)
                if type(x) is tuple:
                    for y in x:
                        # print(type(y))
                        op_list.append(str(type(y))[8:-2]+"()")
        elif type(p) is set:
            for x in p:
                # print(x)
                # if type(x) is tuple:
                #     for y in x:
                #         print(type(y))
                op_list.append(str(type(x))[8:-2]+"()")
                # op_list.append(str(x))
        return
    # print("%s(" % (p.name,))
    op_list.append("%s(" % (p.name,))
    # op_list.append(p.name+'(')
    for k in p:
        # print("%s%s =" % (ind, k,), end=' ')
        op_list.append("%s%s =" % (ind, k,))
        # op_list.append(ind+k+' =')
        get_formal_query_content(p[k],op_list, ind + "    ")
    # print("%s)" % ind)
    op_list.append("%s)" % ind)
    # op_list.append( ind+')')
    # return






def get_query_content(q):
    # print(" ###################### This is the final formalized Query ######################")
    op_list=[]
    # op_list1 = ['b']
    try:
        # op_list=q.algebra
        get_formal_query_content(q.algebra,op_list)
    except AttributeError:
        # it's update, just a list
        for x in q:
            get_formal_query_content(x,op_list)
    # print(" #################################################################")
    # print (op_list)
    return op_list

"""
 Filter all the query content
 in this process i removed all the noisy elements in the query
"""
def filter_content(content_query1):
    query_cont = []
    for x in content_query1:
        # print(x.split( '('))
        # print(x)
        cont=re.split('\(|\)| ',str( x))
        cont.remove('')
        cont=list(filter(('').__ne__, cont))
        query_cont+=cont
        # print(cont)
    return query_cont
" To clculate the cosine similarity of two vectors "
def get_score(v1,v2):
    # print(sqrt(np.dot(v1,v1)))
    # print(sqrt(np.dot(v2, v2)))
    score=(np.dot(v1,v2)/(sqrt(np.dot(v1,v1))*sqrt(np.dot(v2,v2))))
    # print(v1)
    # print(score)
    return score
"Min max normalization of the query vector"
def vector_normalization(list1):
    # print(list1)
    # list2=list1.copy()
    # list1[:] = [number - min(list2) for number in list1]
    # list1=list1/(max(kist2)-min(list1))
    max_v=max(list1)
    min_v=min(list1)
    for i in range(len(list1)):
        list1[i]=(list1[i]-min_v)/(max_v-min_v)
    return list1

" getting and analysing the score "

def queryEquivalenceScore(q1,q2):
    # print(string(q1))
    content_query1=get_query_content(q1)
    content_query2 = get_query_content(q2)

    # print(content_query1)
    filtered_query1_cont=filter_content(content_query1)
    filtered_query2_cont = filter_content(content_query2)


    # print(filtered_query1_cont)
    # print(filtered_query2_cont)
    all_terms=filtered_query1_cont+filtered_query2_cont
    list_dist_terms=list(set(all_terms))
    # print(list_dist_terms)
    query1_vector=[]
    query2_vector = []
    for term in list_dist_terms:

        query1_vector.append(filtered_query1_cont.count(term))
        query2_vector.append(filtered_query2_cont.count(term))

    query1_vector=vector_normalization(query1_vector)
    query2_vector = vector_normalization(query2_vector)
    score=get_score(query1_vector,query2_vector)

    # print(query1_vector)
    # print(query2_vector)

    # print(score)
    score= (score-.70)/(1-.7)
    if score<0:
        return 0
    # print(score)
    return score

