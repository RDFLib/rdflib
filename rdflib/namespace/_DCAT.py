from rdflib.term import URIRef
from rdflib.namespace import DefinedNamespace, Namespace


class DCAT(DefinedNamespace):
    """
    The data catalog vocabulary
    
    DCAT is an RDF vocabulary designed to facilitate interoperability between data catalogs published on the Web.
    By using DCAT to describe datasets in data catalogs, publishers increase discoverability and enable
    applications easily to consume metadata from multiple catalogs. It further enables decentralized publishing of
    catalogs and facilitates federated dataset search across sites. Aggregated DCAT metadata can serve as a
    manifest file to facilitate digital preservation. DCAT is defined at http://www.w3.org/TR/vocab-dcat/. Any
    variance between that normative document and this schema is an error in this schema.
    
    Generated from: https://www.w3.org/ns/dcat2.ttl
    Date: 2020-05-26 14:19:59.985854

    <http://www.w3.org/ns/dcat> rdfs:label "أنطولوجية فهارس قوائم البيانات"@ar
        "Slovník pro datové katalogy"@cs
        "Το λεξιλόγιο των καταλόγων δεδομένων"@el
        "El vocabulario de catálogo de datos"@es
        "Le vocabulaire des jeux de données"@fr
        "Il vocabolario del catalogo dei dati"@it
        "データ・カタログ語彙（DCAT）"@ja
    dct:license <https://creativecommons.org/licenses/by/4.0/>
    dct:modified "2012-04-24"^^xsd:date
        "2013-09-20"^^xsd:date
        "2013-11-28"^^xsd:date
        "2017-12-19"^^xsd:date
        "2019"
    rdfs:comment "هي أنطولوجية تسهل تبادل البيانات بين مختلف الفهارس على الوب. استخدام هذه الأنطولوجية يساعد على
    اكتشاف قوائم  البيانات المنشورة على الوب و يمكن التطبيقات المختلفة من الاستفادة أتوماتيكيا من البيانات المتاحة
    من مختلف الفهارس."@ar
        "DCAT je RDF slovník navržený pro zprostředkování interoperability mezi datovými katalogy publikovanými na
    Webu. Poskytovatelé dat používáním slovníku DCAT pro popis datových sad v datových katalozích zvyšují jejich
    dohledatelnost a umožňují aplikacím konzumovat metadata z více katalogů. Dále je umožňena decentralizovaná
    publikace katalogů a federované dotazování na datové sady napříč katalogy. Agregovaná DCAT metadata mohou také
    sloužit jako průvodka umožňující digitální uchování informace. DCAT je definován na
    http://www.w3.org/TR/vocab-dcat/. Jakýkoliv nesoulad mezi odkazovaným dokumentem a tímto schématem je chybou v
    tomto schématu."@cs
        "Το DCAT είναι ένα RDF λεξιλόγιο που σχεδιάσθηκε για να κάνει εφικτή τη διαλειτουργικότητα μεταξύ
    καταλόγων δεδομένων στον Παγκόσμιο Ιστό. Χρησιμοποιώντας το DCAT για την περιγραφή συνόλων δεδομένων, οι
    εκδότες αυτών αυξάνουν την ανακαλυψιμότητα και επιτρέπουν στις εφαρμογές την εύκολη κατανάλωση μεταδεδομένων
    από πολλαπλούς καταλόγους. Επιπλέον, δίνει τη δυνατότητα για αποκεντρωμένη έκδοση και διάθεση καταλόγων και
    επιτρέπει δυνατότητες ενοποιημένης αναζήτησης μεταξύ διαφορετικών πηγών. Συγκεντρωτικά μεταδεδομένα που έχουν
    περιγραφεί με το DCAT μπορούν να χρησιμοποιηθούν σαν ένα δηλωτικό αρχείο (manifest file) ώστε να διευκολύνουν
    την ψηφιακή συντήρηση."@el
        "DCAT es un vocabulario RDF diseñado para facilitar la interoperabilidad entre catálogos de datos
    publicados en la Web. Utilizando DCAT para describir datos disponibles en catálogos se aumenta la posibilidad
    de que sean descubiertos y se permite que las aplicaciones consuman fácilmente los metadatos de varios
    catálogos."@es
        "DCAT est un vocabulaire développé pour faciliter l'interopérabilité entre les jeux de données publiées
    sur le Web. En utilisant DCAT pour décrire les jeux de données dans les catalogues de données, les
    fournisseurs de données augmentent leur découverte et permettent que les applications facilement les
    métadonnées de plusieurs catalogues. Il permet en plus la publication décentralisée des catalogues et
    facilitent la recherche fédérée des données entre plusieurs sites. Les métadonnées DCAT aggrégées peuvent
    servir comme un manifeste pour faciliter la préservation digitale des ressources. DCAT est définie à l'adresse
    http://www.w3.org/TR/vocab-dcat/. Une quelconque version de ce document normatif et ce vocabulaire est une
    erreur dans ce vocabulaire."@fr
        "DCAT è un vocabolario RDF progettato per facilitare l'interoperabilità tra i cataloghi di dati pubblicati
    nel Web. Utilizzando DCAT per descrivere i dataset nei cataloghi di dati, i fornitori migliorano la capacità
    di individuazione dei dati e abilitano le  applicazioni al consumo di dati provenienti da cataloghi
    differenti. DCAT permette di decentralizzare la pubblicazione di cataloghi e facilita la ricerca federata dei
    dataset. L'aggregazione dei metadati federati può fungere da file manifesto per facilitare la conservazione
    digitale. DCAT è definito all'indirizzo http://www.w3.org/TR/vocab-dcat/. Qualsiasi scostamento tra tale
    definizione normativa e questo schema è da considerarsi un errore di questo schema."@it
        "DCATは、ウェブ上で公開されたデータ・カタログ間の相互運用性の促進を目的とするRDFの語彙です。このドキュメントでは、その利用のために、スキーマを定義し、例を提供します。データ・カタログ内のデータセットを記述
    するためにDCATを用いると、公開者が、発見可能性を増加させ、アプリケーションが複数のカタログのメタデータを容易に利用できるようになります。さらに、カタログの分散公開を可能にし、複数のサイトにまたがるデータセットの統合検
    索を促進します。集約されたDCATメタデータは、ディジタル保存を促進するためのマニフェスト・ファイルとして使用できます。"@ja
    owl:imports dct:
        <http://www.w3.org/2004/02/skos/core>
        <http://www.w3.org/ns/prov-o#>
    owl:versionInfo "Toto je aktualizovaná kopie slovníku DCAT verze 2.0, převzatá z
    https://www.w3.org/ns/dcat.ttl"@cs
        "Questa è una copia aggiornata del vocabolario DCAT v2.0 disponibile in https://www.w3.org/ns/dcat.ttl"
        "This is an updated copy of v2.0 of the DCAT vocabulary, taken from https://www.w3.org/ns/dcat.ttl"
        "Esta es una copia del vocabulario DCAT v2.0 disponible en https://www.w3.org/ns/dcat.ttl"@es
    skos:editorialNote "English language definitions updated in this revision in line with ED. Multilingual text
    unevenly updated."
    """
    
    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property
    accessURL: URIRef               # A URL of a resource that gives access to a distribution of the dataset. E.g. landing page, feed, SPARQL endpoint. Use for all cases except a simple download link, in which case downloadURL is preferred.
    bbox: URIRef                    # The geographic bounding box of a resource.
    byteSize: URIRef                # The size of a distribution in bytes.
    centroid: URIRef                # The geographic center (centroid) of a resource.
    compressFormat: URIRef          # The compression format of the distribution in which the data is contained in a compressed form, e.g. to reduce the size of the downloadable file.
    contactPoint: URIRef            # Relevant contact information for the catalogued resource. Use of vCard is recommended.
    dataset: URIRef                 # A collection of data that is listed in the catalog.
    distribution: URIRef            # An available distribution of the dataset.
    downloadURL: URIRef             # The URL of the downloadable file in a given format. E.g. CSV file or RDF file. The format is indicated by the distribution's dct:format and/or dcat:mediaType.
    endDate: URIRef                 # The end of the period.
    keyword: URIRef                 # A keyword or tag describing a resource.
    landingPage: URIRef             # A Web page that can be navigated to in a Web browser to gain access to the catalog, a dataset, its distributions and/or additional information.
    mediaType: URIRef               # The media type of the distribution as defined by IANA.
    packageFormat: URIRef           # The package format of the distribution in which one or more data files are grouped together, e.g. to enable a set of related files to be downloaded together.
    record: URIRef                  # A record describing the registration of a single dataset or data service that is part of the catalog.
    startDate: URIRef               # The start of the period
    theme: URIRef                   # A main category of the resource. A resource can have multiple themes.
    themeTaxonomy: URIRef           # The knowledge organization system (KOS) used to classify catalog's datasets.

    # http://www.w3.org/2000/01/rdf-schema#Class
    Catalog: URIRef                 # A curated collection of metadata about resources (e.g., datasets and data services in the context of a data catalog).
    CatalogRecord: URIRef           # A record in a data catalog, describing the registration of a single dataset or data service.
    Dataset: URIRef                 # A collection of data, published or curated by a single source, and available for access or download in one or more represenations.
    Distribution: URIRef            # A specific representation of a dataset. A dataset might be available in multiple serializations that may differ in various ways, including natural language, media-type or format, schematic organization, temporal and spatial resolution, level of detail or profiles (which might specify any or all of the above).

    # http://www.w3.org/2002/07/owl#Class
    DataService: URIRef             # A site or end-point providing operations related to the discovery of, access to, or processing functions on, data or related resources.
    Relationship: URIRef            # An association class for attaching additional information to a relationship between DCAT Resources.
    Resource: URIRef                # Resource published or curated by a single agent.
    Role: URIRef                    # A role is the function of a resource or agent with respect to another resource, in the context of resource attribution or resource relationships.

    # http://www.w3.org/2002/07/owl#DatatypeProperty
    spatialResolutionInMeters: URIRef  # mínima separacíon espacial disponible en un conjunto de datos, medida en metros.
    temporalResolution: URIRef      # minimum time period resolvable in a dataset.

    # http://www.w3.org/2002/07/owl#ObjectProperty
    accessService: URIRef           # A site or end-point that gives access to the distribution of the dataset.
    catalog: URIRef                 # A catalog whose contents are of interest in the context of this catalog.
    endpointDescription: URIRef     # A description of the service end-point, including its operations, parameters etc.
    endpointURL: URIRef             # The root location or primary endpoint of the service (a web-resolvable IRI).
    hadRole: URIRef                 # The function of an entity or agent with respect to another entity or resource.
    qualifiedRelation: URIRef       # Link to a description of a relationship with another resource.
    servesDataset: URIRef           # A collection of data that this DataService can distribute.
    service: URIRef                 # A site or endpoint that is listed in the catalog.

    _NS = Namespace("http://www.w3.org/ns/dcat#")
