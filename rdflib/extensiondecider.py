
class PathException(Exception):
	pass

class NoFileException(PathException):#exception for no file name given as parameter
	pass

class NoFileExtensionException(PathException):#exception for no file extension in the file name
	pass

class NoParseForJsonLdException(PathException):#parser for jsonld not available in rdflib
	pass

#for finding the format of the file irrespective of its extension and return two parameter one correct file name and its format
#use these parameters in graph.parse()
def check_extension(fpath):

	if(fpath==""):#parameter is empty
	
		raise NoFileException()
	
	else:
	
		if "." in fpath:
	
			pathsplit = fpath.split(".")
	
			if len(pathsplit)==1 :#no file extension present
				raise NoFileExtensionException()
			
			else:
				# for each extension now checking whether the format of the content in the file matches the the extension of the file
				if pathsplit[-1]=="ttl":
					s = decide_ext(fpath)#get the format for given file
					if s=="ttl":#if it matches the extension then return
						return fpath , 'ttl'
					else:#if not then create a new file with proper extension and return its name and format
						print("wrong extension")
						filename = convertfile(fpath,s)#create a new file with proper extension
						return filename , s

				elif pathsplit[-1]=="n3":
					s = decide_ext(fpath)#get the format for given file
					if s=="ttl":#if it matches the extension then return
						return fpath,'n3'
					else:#if not then create a new file with proper extension and return its name and format
						print("wrong extension")
						filename = convertfile(fpath,s)
						return filename , s

				elif pathsplit[-1]=="nt":
					s = decide_ext(fpath)
					if s=="nt":
						return fpath , 'nt'
					else:
						print("wrong extension")
						filename = convertfile(fpath,s)
						return filename , s

				elif pathsplit[-1]=="trig":
					s = decide_ext(fpath)
					if s=="trig" or s == "ttl":
						return fpath, 'trig'						
					else:
						print("wrong extension")
						filename = convertfile(fpath,s)
						return filename , s

				elif pathsplit[-1]=="rdf":
					s = decide_ext(fpath)
					if s=="rdf":
						return fpath , 'application/rdf+xml'
					else:
						print("wrong extension")
						filename = convertfile(fpath,s)
						return filename , s
						
				elif pathsplit[-1]=="nq":
					s = decide_ext(fpath)
					if s=="nq":
						return fpath , 'nq'
					else:
						print("wrong extension")
						filename = convertfile(fpath,s)
						return filename , s

				elif pathsplit[-1]=="jsonld":
					s = decide_ext(fpath)
					if s=="jsonld":
						raise NoParseForJsonLdException()#jsonld parser not available
					else:
						print("wrong extension")
						filename = convertfile(fpath,s)
						return filename , s
						
				else:#any other extension and finding the correct format of the content in them
					s = decide_ext(fpath)
					print("wrong extension")
					filename = convertfile(fpath,s)
					return filename , s

		else:
			raise NoFileException()


def decide_ext(fpath):#finding the extension of the contents in the file

	f1 = open(fpath,"r")
	
	s=f1.read()
	f1.close()
	s = s.split("\n")#getting each line from the file

	for i in range(len(s)):

		if s[i]!="\n" and s[i]!="":#first value of the content

			if "{" in s[i]:
				print("jsonld")
				return "jsonld"
			
			elif "<rdf" in s[i] or "<?xml" in s[i] :
				print("rdf/xml")
				return "rdf"
			
			elif "@prefix" in s[i]:
				print("turtle family")
				return whichturlefamily(s)#decide whether it is trig or turtle
			
			else:
				# s1 = s[i].split(" ")
				# if s1[0][0]!='<':
				# 	print("cannot determine type")
				
				for j in range(i,len(s)):
					s1 = s[j].split(" ")
					
					for k in range(len(s1)-1):
						
						if s1[k][0]!='<' and s1[k][0]!='"' and s1[k][0]!='.':
							
							if s1[k+1][0]=="<": 
								print("turtle family")#it is part of the turtle family and deciding trig or turtle

								return whichturlefamily(s)
							break

				for j in range(i,len(s)):
					s1 = s[j].split("> ")
					if len(s1)<4:#if having 4 nodes then N-Quads else N-Triples
						print("N-Triples")
						return ("nt")

				print("N-Quads")
				return "nq"

	f1.close()

def whichturlefamily(s):#determining turtle or trig
	for i in range(len(s)):
		if "GRAPH <" in s[i]:
			return "trig"

	return "ttl"

def convertfile(fpath,ext):#coppying file with content not matching the extension to one with proper extension
	f1 = open(fpath,"r")
	s=f1.read()
	f1.close()

	filepath = fpath.split(".")
	newfilepath = ""
	for i in range(len(filepath)-1):#creating the new filename with proper extension
		newfilepath = newfilepath+filepath[i]

	newfilepath=newfilepath+"."+ext

	f1 = open(newfilepath,"w")
	f1.write(s)
	f1.close()
	return newfilepath


# print(check_extension("projectext.rdf"))