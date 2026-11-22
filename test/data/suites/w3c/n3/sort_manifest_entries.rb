# Sorts the entries in a manifest in text blocks, skipping the manifest

raw_man = File.read(ARGV[0])

preamble, entries = raw_man.split(/\s+\) \.$/, 2)

puts preamble + "\n  ) ."

entries.split(/^\s*$/m).map(&:strip).sort.each do |e|
  puts e
  puts
end
