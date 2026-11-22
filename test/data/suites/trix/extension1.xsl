<?xml version="1.0"?>
<!-- Replaces any XML document by a hard-coded TriX document containing
	one graph with one triple -->
<xsl:stylesheet 
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns="http://www.w3.org/2004/03/trix/trix-1/"
		xmlns:ex="http://example.com/#"
		version="2.0">
	<xsl:template match="/">
		<TriX>
			<graph>
				<triple>
					<qname>ex:a</qname>
					<qname>ex:b</qname>
					<qname>ex:c</qname>
				</triple>
			</graph>
		</TriX>
	</xsl:template>
</xsl:stylesheet>