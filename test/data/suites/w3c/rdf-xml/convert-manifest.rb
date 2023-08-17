#!/usr/bin/env ruby
# Convert 2004 manifest to 2013 format and vocabulary
require 'linkeddata'
require 'fileutils'

TEST = RDF::Vocabulary.new("http://www.w3.org/2000/10/rdf-tests/rdfcore/testSchema#")
QUERY = SPARQL.parse(%(
  PREFIX test: <http://www.w3.org/2000/10/rdf-tests/rdfcore/testSchema#>
  SELECT ?subject ?type ?description ?action ?result
  WHERE {
    ?subject a ?type;
      test:status "APPROVED";
      test:inputDocument ?action;
      OPTIONAL {
        ?subject test:description ?description
      }
      OPTIONAL {
        ?subject test:outputDocument ?result
      }
    FILTER(?type = test:PositiveParserTest || ?type = test:NegativeParserTest)
  }
))

g = RDF::Repository.load("2004-test-suite/Manifest.rdf")

tests = {}

File.open("manifest.ttl", "w") do |f|
  f.write(%(
    # RDF/XML Syntax tests
    ## Distributed under both the W3C Test Suite License[1] and the W3C 3-
    ## clause BSD License[2]. To contribute to a W3C Test Suite, see the
    ## policies and contribution forms [3]
    ##
    ## 1. http://www.w3.org/Consortium/Legal/2008/04-testsuite-license
    ## 2. http://www.w3.org/Consortium/Legal/2008/03-bsd-license
    ## 3. http://www.w3.org/2004/10/27-testcases
    
    @prefix rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix mf: <http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#> .
    @prefix rdft:   <http://www.w3.org/ns/rdftest#> .

    <> rdf:type mf:Manifest ;
      rdfs:comment "RDF/XML Syntax tests" ;
      mf:entries \()[1..-1].gsub(/^    /, ''))

  QUERY.execute(g).each do |soln|
    #puts soln.inspect
    dir = soln.subject.path.split('/')[-2]
    frag = "##{dir}-#{soln.subject.fragment}"
    puts "test #{dir}/'#{frag}' already defined" if tests.has_key?(frag)
    f.write("\n    <#{frag}>")
    tests[frag] = soln
  end
  f.puts("\n  ) .\n\n")

  tests.each_pair do |frag, test|
    raise "test #{frag} missing description" unless test[:description]
    # Wrap description to 40 characters and indent
    desc = test.description.
      to_s.
      strip.
      gsub(/\s+/m, ' ').
      scan(/\S.{0,60}\S(?=\s|$)|\S+/).
      join("\n    ")

    type = test.type.fragment == "PositiveParserTest" ? "TestXMLEval" : "TestXMLNegativeSyntax"

    test_desc = %(
    <#{frag}> a rdft:#{type};
      mf:name "#{frag[1..-1]}";
      rdfs:comment """
        #{desc}
      """;
      rdfs:approval rdft:Approved
    ).gsub(/^    /, '')[1..-2]

    [:action, :result].each do |t|
      next unless test[t]
      path = test[t].path.split('/')[-2..-1].join('/')

      # Copy the test into place, if it does not exist.
      parts = path.split('/')

      FileUtils.mkdir(parts.first) unless Dir.exist?(parts.first)
      puts "Copy 2004-test-suite/#{path} to #{path}"
      FileUtils.cp "2004-test-suite/#{path}", path
      test_desc += ";\n  mf:#{t} <#{path}>"
    end
    test_desc += " .\n\n"

    f.puts test_desc
  end
end

