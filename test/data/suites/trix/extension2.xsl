<?xml version="1.0"?>
<!-- Expands <qname>ns:foo</qname> to <uri>.....foo</uri> using xmlns:ns -->
<xsl:stylesheet 
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns="http://www.w3.org/2004/03/trix/trix-1/"
		xmlns:trix="http://www.w3.org/2004/03/trix/trix-1/"
		xmlns:ex="http://example.com/#"
		version="2.0">

	<!-- Expand qnames -->
	<xsl:template match="trix:qname">
		<uri>
			<xsl:variable name="ns">
				<xsl:value-of select="substring-before(text(),':')"/>
			</xsl:variable>
			<xsl:value-of select="namespace::*[local-name()=$ns]"/>
			<xsl:value-of select="substring-after(text(),':')"/>
		</uri>
	</xsl:template>

	<!-- Not necessary, but avoids namespace declarations scattered through
		the result document -->
	<xsl:template match="trix:TriX">
		<TriX><xsl:apply-templates/></TriX>
	</xsl:template>

	<!-- This is a simple identity function -->
	<xsl:template match="@*|*|processing-instruction()|comment()" priority="-2">
		<xsl:copy>
			<xsl:apply-templates select="*|@*|text()|processing-instruction()|comment()"/>
		</xsl:copy>
	</xsl:template>
</xsl:stylesheet>