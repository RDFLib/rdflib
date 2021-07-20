from rdflib.term import URIRef
from rdflib.namespace import DefinedNamespace, Namespace


class SDO(DefinedNamespace):
    """
    Generated from: http://schema.org/version/latest/schema.ttl
    Date: 2020-05-26 14:20:07.348101

    """

    # http://schema.org/ActionStatusType
    ActiveActionStatus: URIRef  # An in-progress action (e.g, while watching the movie, or driving to a location).
    CompletedActionStatus: URIRef  # An action that has already taken place.
    FailedActionStatus: URIRef  # An action that failed to complete. The action's error property and the HTTP return code contain more information about the failure.
    PotentialActionStatus: URIRef  # A description of an action that is supported.

    # http://schema.org/Audience
    Researcher: URIRef  # Researchers.

    # http://schema.org/BoardingPolicyType
    GroupBoardingPolicy: URIRef  # The airline boards by groups based on check-in time, priority, etc.
    ZoneBoardingPolicy: URIRef  # The airline boards by zones of the plane.

    # http://schema.org/BookFormatType
    AudiobookFormat: URIRef  # Book format: Audiobook. This is an enumerated value for use with the bookFormat property. There is also a type 'Audiobook' in the bib extension which includes Audiobook specific properties.
    EBook: URIRef  # Book format: Ebook.
    Hardcover: URIRef  # Book format: Hardcover.
    Paperback: URIRef  # Book format: Paperback.

    # http://schema.org/Boolean

    # http://schema.org/ContactPointOption
    HearingImpairedSupported: URIRef  # Uses devices to support users with hearing impairments.
    TollFree: URIRef  # The associated telephone number is toll free.

    # http://schema.org/DayOfWeek
    Friday: URIRef  # The day of the week between Thursday and Saturday.
    Monday: URIRef  # The day of the week between Sunday and Tuesday.
    PublicHolidays: URIRef  # This stands for any day that is a public holiday; it is a placeholder for all official public holidays in some particular location. While not technically a "day of the week", it can be used with <a class="localLink" href="http://schema.org/OpeningHoursSpecification">OpeningHoursSpecification</a>. In the context of an opening hours specification it can be used to indicate opening hours on public holidays, overriding general opening hours for the day of the week on which a public holiday occurs.
    Saturday: URIRef  # The day of the week between Friday and Sunday.
    Sunday: URIRef  # The day of the week between Saturday and Monday.
    Thursday: URIRef  # The day of the week between Wednesday and Friday.
    Tuesday: URIRef  # The day of the week between Monday and Wednesday.
    Wednesday: URIRef  # The day of the week between Tuesday and Thursday.

    # http://schema.org/DeliveryMethod
    OnSitePickup: URIRef  # A DeliveryMethod in which an item is collected on site, e.g. in a store or at a box office.

    # http://schema.org/DigitalDocumentPermissionType
    CommentPermission: URIRef  # Permission to add comments to the document.
    ReadPermission: URIRef  # Permission to read or view the document.
    WritePermission: URIRef  # Permission to write or edit the document.

    # http://schema.org/DriveWheelConfigurationValue
    AllWheelDriveConfiguration: URIRef  # All-wheel Drive is a transmission layout where the engine drives all four wheels.
    FourWheelDriveConfiguration: URIRef  # Four-wheel drive is a transmission layout where the engine primarily drives two wheels with a part-time four-wheel drive capability.
    FrontWheelDriveConfiguration: URIRef  # Front-wheel drive is a transmission layout where the engine drives the front wheels.
    RearWheelDriveConfiguration: URIRef  # Real-wheel drive is a transmission layout where the engine drives the rear wheels.

    # http://schema.org/EventStatusType
    EventCancelled: URIRef  # The event has been cancelled. If the event has multiple startDate values, all are assumed to be cancelled. Either startDate or previousStartDate may be used to specify the event's cancelled date(s).
    EventMovedOnline: URIRef  # Indicates that the event was changed to allow online participation. See <a class="localLink" href="http://schema.org/eventAttendanceMode">eventAttendanceMode</a> for specifics of whether it is now fully or partially online.
    EventPostponed: URIRef  # The event has been postponed and no new date has been set. The event's previousStartDate should be set.
    EventRescheduled: URIRef  # The event has been rescheduled. The event's previousStartDate should be set to the old date and the startDate should be set to the event's new date. (If the event has been rescheduled multiple times, the previousStartDate property may be repeated).
    EventScheduled: URIRef  # The event is taking place or has taken place on the startDate as scheduled. Use of this value is optional, as it is assumed by default.

    # http://schema.org/GamePlayMode
    CoOp: URIRef  # Play mode: CoOp. Co-operative games, where you play on the same team with friends.
    MultiPlayer: URIRef  # Play mode: MultiPlayer. Requiring or allowing multiple human players to play simultaneously.
    SinglePlayer: URIRef  # Play mode: SinglePlayer. Which is played by a lone player.

    # http://schema.org/GameServerStatus
    OfflinePermanently: URIRef  # Game server status: OfflinePermanently. Server is offline and not available.
    OfflineTemporarily: URIRef  # Game server status: OfflineTemporarily. Server is offline now but it can be online soon.
    Online: URIRef  # Game server status: Online. Server is available.
    OnlineFull: URIRef  # Game server status: OnlineFull. Server is online but unavailable. The maximum number of players has reached.

    # http://schema.org/GenderType
    Female: URIRef  # The female gender.
    Male: URIRef  # The male gender.

    # http://schema.org/ItemAvailability
    Discontinued: URIRef  # Indicates that the item has been discontinued.
    InStock: URIRef  # Indicates that the item is in stock.
    InStoreOnly: URIRef  # Indicates that the item is available only at physical locations.
    LimitedAvailability: URIRef  # Indicates that the item has limited availability.
    OnlineOnly: URIRef  # Indicates that the item is available only online.
    OutOfStock: URIRef  # Indicates that the item is out of stock.
    PreOrder: URIRef  # Indicates that the item is available for pre-order.
    PreSale: URIRef  # Indicates that the item is available for ordering and delivery before general availability.
    SoldOut: URIRef  # Indicates that the item has sold out.

    # http://schema.org/ItemListOrderType
    ItemListOrderAscending: URIRef  # An ItemList ordered with lower values listed first.
    ItemListOrderDescending: URIRef  # An ItemList ordered with higher values listed first.
    ItemListUnordered: URIRef  # An ItemList ordered with no explicit order.

    # http://schema.org/MapCategoryType
    ParkingMap: URIRef  # A parking map.
    SeatingMap: URIRef  # A seating map.
    TransitMap: URIRef  # A transit map.
    VenueMap: URIRef  # A venue map (e.g. for malls, auditoriums, museums, etc.).

    # http://schema.org/MusicAlbumProductionType
    CompilationAlbum: URIRef  # CompilationAlbum.
    DJMixAlbum: URIRef  # DJMixAlbum.
    DemoAlbum: URIRef  # DemoAlbum.
    LiveAlbum: URIRef  # LiveAlbum.
    MixtapeAlbum: URIRef  # MixtapeAlbum.
    RemixAlbum: URIRef  # RemixAlbum.
    SoundtrackAlbum: URIRef  # SoundtrackAlbum.
    SpokenWordAlbum: URIRef  # SpokenWordAlbum.
    StudioAlbum: URIRef  # StudioAlbum.

    # http://schema.org/MusicAlbumReleaseType
    AlbumRelease: URIRef  # AlbumRelease.
    BroadcastRelease: URIRef  # BroadcastRelease.
    EPRelease: URIRef  # EPRelease.
    SingleRelease: URIRef  # SingleRelease.

    # http://schema.org/MusicReleaseFormatType
    CDFormat: URIRef  # CDFormat.
    CassetteFormat: URIRef  # CassetteFormat.
    DVDFormat: URIRef  # DVDFormat.
    DigitalAudioTapeFormat: URIRef  # DigitalAudioTapeFormat.
    DigitalFormat: URIRef  # DigitalFormat.
    LaserDiscFormat: URIRef  # LaserDiscFormat.
    VinylFormat: URIRef  # VinylFormat.

    # http://schema.org/OfferItemCondition
    DamagedCondition: URIRef  # Indicates that the item is damaged.
    NewCondition: URIRef  # Indicates that the item is new.
    RefurbishedCondition: URIRef  # Indicates that the item is refurbished.
    UsedCondition: URIRef  # Indicates that the item is used.

    # http://schema.org/OrderStatus
    OrderCancelled: URIRef  # OrderStatus representing cancellation of an order.
    OrderDelivered: URIRef  # OrderStatus representing successful delivery of an order.
    OrderInTransit: URIRef  # OrderStatus representing that an order is in transit.
    OrderPaymentDue: URIRef  # OrderStatus representing that payment is due on an order.
    OrderPickupAvailable: URIRef  # OrderStatus representing availability of an order for pickup.
    OrderProblem: URIRef  # OrderStatus representing that there is a problem with the order.
    OrderProcessing: URIRef  # OrderStatus representing that an order is being processed.
    OrderReturned: URIRef  # OrderStatus representing that an order has been returned.

    # http://schema.org/PaymentStatusType
    PaymentAutomaticallyApplied: URIRef  # An automatic payment system is in place and will be used.
    PaymentComplete: URIRef  # The payment has been received and processed.
    PaymentDeclined: URIRef  # The payee received the payment, but it was declined for some reason.
    PaymentDue: URIRef  # The payment is due, but still within an acceptable time to be received.
    PaymentPastDue: URIRef  # The payment is due and considered late.

    # http://schema.org/ReservationStatusType
    ReservationCancelled: URIRef  # The status for a previously confirmed reservation that is now cancelled.
    ReservationConfirmed: URIRef  # The status of a confirmed reservation.
    ReservationHold: URIRef  # The status of a reservation on hold pending an update like credit card number or flight changes.
    ReservationPending: URIRef  # The status of a reservation when a request has been sent, but not confirmed.

    # http://schema.org/RestrictedDiet
    DiabeticDiet: URIRef  # A diet appropriate for people with diabetes.
    GlutenFreeDiet: URIRef  # A diet exclusive of gluten.
    HalalDiet: URIRef  # A diet conforming to Islamic dietary practices.
    HinduDiet: URIRef  # A diet conforming to Hindu dietary practices, in particular, beef-free.
    KosherDiet: URIRef  # A diet conforming to Jewish dietary practices.
    LowCalorieDiet: URIRef  # A diet focused on reduced calorie intake.
    LowFatDiet: URIRef  # A diet focused on reduced fat and cholesterol intake.
    LowLactoseDiet: URIRef  # A diet appropriate for people with lactose intolerance.
    LowSaltDiet: URIRef  # A diet focused on reduced sodium intake.
    VeganDiet: URIRef  # A diet exclusive of all animal products.
    VegetarianDiet: URIRef  # A diet exclusive of animal meat.

    # http://schema.org/RsvpResponseType
    RsvpResponseMaybe: URIRef  # The invitee may or may not attend.
    RsvpResponseNo: URIRef  # The invitee will not attend.
    RsvpResponseYes: URIRef  # The invitee will attend.

    # http://schema.org/SteeringPositionValue
    LeftHandDriving: URIRef  # The steering position is on the left side of the vehicle (viewed from the main direction of driving).
    RightHandDriving: URIRef  # The steering position is on the right side of the vehicle (viewed from the main direction of driving).

    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property
    about: URIRef  # The subject matter of the content.
    acceptedAnswer: URIRef  # The answer(s) that has been accepted as best, typically on a Question/Answer site. Sites vary in their selection mechanisms, e.g. drawing on community opinion and/or the view of the Question author.
    acceptedOffer: URIRef  # The offer(s) -- e.g., product, quantity and price combinations -- included in the order.
    acceptedPaymentMethod: URIRef  # The payment method(s) accepted by seller for this offer.
    acceptsReservations: URIRef  # Indicates whether a FoodEstablishment accepts reservations. Values can be Boolean, an URL at which reservations can be made or (for backwards compatibility) the strings <code>Yes</code> or <code>No</code>.
    accessCode: URIRef  # Password, PIN, or access code needed for delivery (e.g. from a locker).
    accessMode: URIRef  # The human sensory perceptual system or cognitive faculty through which a person may process or perceive information. Expected values include: auditory, tactile, textual, visual, colorDependent, chartOnVisual, chemOnVisual, diagramOnVisual, mathOnVisual, musicOnVisual, textOnVisual.
    accessModeSufficient: URIRef  # A list of single or combined accessModes that are sufficient to understand all the intellectual content of a resource. Expected values include:  auditory, tactile, textual, visual.
    accessibilityAPI: URIRef  # Indicates that the resource is compatible with the referenced accessibility API (<a href="http://www.w3.org/wiki/WebSchemas/Accessibility">WebSchemas wiki lists possible values</a>).
    accessibilityControl: URIRef  # Identifies input methods that are sufficient to fully control the described resource (<a href="http://www.w3.org/wiki/WebSchemas/Accessibility">WebSchemas wiki lists possible values</a>).
    accessibilityFeature: URIRef  # Content features of the resource, such as accessible media, alternatives and supported enhancements for accessibility (<a href="http://www.w3.org/wiki/WebSchemas/Accessibility">WebSchemas wiki lists possible values</a>).
    accessibilityHazard: URIRef  # A characteristic of the described resource that is physiologically dangerous to some users. Related to WCAG 2.0 guideline 2.3 (<a href="http://www.w3.org/wiki/WebSchemas/Accessibility">WebSchemas wiki lists possible values</a>).
    accessibilitySummary: URIRef  # A human-readable summary of specific accessibility features or deficiencies, consistent with the other accessibility metadata but expressing subtleties such as "short descriptions are present but long descriptions will be needed for non-visual users" or "short descriptions are present and no long descriptions are needed."
    accountId: URIRef  # The identifier for the account the payment will be applied to.
    accountablePerson: URIRef  # Specifies the Person that is legally accountable for the CreativeWork.
    acquiredFrom: URIRef  # The organization or person from which the product was acquired.
    actionAccessibilityRequirement: URIRef  # A set of requirements that a must be fulfilled in order to perform an Action. If more than one value is specied, fulfilling one set of requirements will allow the Action to be performed.
    actionApplication: URIRef  # An application that can complete the request.
    actionOption: URIRef  # A sub property of object. The options subject to this action.
    actionPlatform: URIRef  # The high level platform(s) where the Action can be performed for the given URL. To specify a specific application or operating system instance, use actionApplication.
    actionStatus: URIRef  # Indicates the current disposition of the Action.
    actor: URIRef  # An actor, e.g. in tv, radio, movie, video games etc., or in an event. Actors can be associated with individual items or with a series, episode, clip.
    actors: URIRef  # An actor, e.g. in tv, radio, movie, video games etc. Actors can be associated with individual items or with a series, episode, clip.
    addOn: URIRef  # An additional offer that can only be obtained in combination with the first base offer (e.g. supplements and extensions that are available for a surcharge).
    additionalName: URIRef  # An additional name for a Person, can be used for a middle name.
    additionalNumberOfGuests: URIRef  # If responding yes, the number of guests who will attend in addition to the invitee.
    additionalProperty: URIRef  # A property-value pair representing an additional characteristics of the entitity, e.g. a product feature or another characteristic for which there is no matching property in schema.org.<br/><br/>  Note: Publishers should be aware that applications designed to use specific schema.org properties (e.g. http://schema.org/width, http://schema.org/color, http://schema.org/gtin13, ...) will typically expect such data to be provided using those properties, rather than using the generic property/value mechanism.
    additionalType: URIRef  # An additional type for the item, typically used for adding more specific types from external vocabularies in microdata syntax. This is a relationship between something and a class that the thing is in. In RDFa syntax, it is better to use the native RDFa syntax - the 'typeof' attribute - for multiple types. Schema.org tools may have only weaker understanding of extra types, in particular those defined externally.
    address: URIRef  # Physical address of the item.
    addressCountry: URIRef  # The country. For example, USA. You can also provide the two-letter <a href="http://en.wikipedia.org/wiki/ISO_3166-1">ISO 3166-1 alpha-2 country code</a>.
    addressLocality: URIRef  # The locality in which the street address is, and which is in the region. For example, Mountain View.
    addressRegion: URIRef  # The region in which the locality is, and which is in the country. For example, California or another appropriate first-level <a href="https://en.wikipedia.org/wiki/List_of_administrative_divisions_by_country">Administrative division</a>
    advanceBookingRequirement: URIRef  # The amount of time that is required between accepting the offer and the actual usage of the resource or service.
    affiliation: URIRef  # An organization that this person is affiliated with. For example, a school/university, a club, or a team.
    afterMedia: URIRef  # A media object representing the circumstances after performing this direction.
    agent: URIRef  # The direct performer or driver of the action (animate or inanimate). e.g. <em>John</em> wrote a book.
    aggregateRating: URIRef  # The overall rating, based on a collection of reviews or ratings, of the item.
    aircraft: URIRef  # The kind of aircraft (e.g., "Boeing 747").
    album: URIRef  # A music album.
    albumProductionType: URIRef  # Classification of the album by it's type of content: soundtrack, live album, studio album, etc.
    albumRelease: URIRef  # A release of this album.
    albumReleaseType: URIRef  # The kind of release which this album is: single, EP or album.
    albums: URIRef  # A collection of music albums.
    alignmentType: URIRef  # A category of alignment between the learning resource and the framework node. Recommended values include: 'requires', 'textComplexity', 'readingLevel', and 'educationalSubject'.
    alternateName: URIRef  # An alias for the item.
    alternativeHeadline: URIRef  # A secondary title of the CreativeWork.
    alumni: URIRef  # Alumni of an organization.
    alumniOf: URIRef  # An organization that the person is an alumni of.
    amenityFeature: URIRef  # An amenity feature (e.g. a characteristic or service) of the Accommodation. This generic property does not make a statement about whether the feature is included in an offer for the main accommodation or available at extra costs.
    amount: URIRef  # The amount of money.
    amountOfThisGood: URIRef  # The quantity of the goods included in the offer.
    annualPercentageRate: URIRef  # The annual rate that is charged for borrowing (or made by investing), expressed as a single percentage number that represents the actual yearly cost of funds over the term of a loan. This includes any fees or additional costs associated with the transaction.
    answerCount: URIRef  # The number of answers this question has received.
    application: URIRef  # An application that can complete the request.
    applicationCategory: URIRef  # Type of software application, e.g. 'Game, Multimedia'.
    applicationSubCategory: URIRef  # Subcategory of the application, e.g. 'Arcade Game'.
    applicationSuite: URIRef  # The name of the application suite to which the application belongs (e.g. Excel belongs to Office).
    appliesToDeliveryMethod: URIRef  # The delivery method(s) to which the delivery charge or payment charge specification applies.
    appliesToPaymentMethod: URIRef  # The payment method(s) to which the payment charge specification applies.
    area: URIRef  # The area within which users can expect to reach the broadcast service.
    areaServed: URIRef  # The geographic area where a service or offered item is provided.
    arrivalAirport: URIRef  # The airport where the flight terminates.
    arrivalBusStop: URIRef  # The stop or station from which the bus arrives.
    arrivalGate: URIRef  # Identifier of the flight's arrival gate.
    arrivalPlatform: URIRef  # The platform where the train arrives.
    arrivalStation: URIRef  # The station where the train trip ends.
    arrivalTerminal: URIRef  # Identifier of the flight's arrival terminal.
    arrivalTime: URIRef  # The expected arrival time.
    artEdition: URIRef  # The number of copies when multiple copies of a piece of artwork are produced - e.g. for a limited edition of 20 prints, 'artEdition' refers to the total number of copies (in this example "20").
    artMedium: URIRef  # The material used. (e.g. Oil, Watercolour, Acrylic, Linoprint, Marble, Cyanotype, Digital, Lithograph, DryPoint, Intaglio, Pastel, Woodcut, Pencil, Mixed Media, etc.)
    artform: URIRef  # e.g. Painting, Drawing, Sculpture, Print, Photograph, Assemblage, Collage, etc.
    articleBody: URIRef  # The actual body of the article.
    articleSection: URIRef  # Articles may belong to one or more 'sections' in a magazine or newspaper, such as Sports, Lifestyle, etc.
    artworkSurface: URIRef  # The supporting materials for the artwork, e.g. Canvas, Paper, Wood, Board, etc.
    assembly: URIRef  # Library file name e.g., mscorlib.dll, system.web.dll.
    assemblyVersion: URIRef  # Associated product/technology version. e.g., .NET Framework 4.5.
    associatedArticle: URIRef  # A NewsArticle associated with the Media Object.
    associatedMedia: URIRef  # A media object that encodes this CreativeWork. This property is a synonym for encoding.
    athlete: URIRef  # A person that acts as performing member of a sports team; a player as opposed to a coach.
    attendee: URIRef  # A person or organization attending the event.
    attendees: URIRef  # A person attending the event.
    audience: URIRef  # An intended audience, i.e. a group for whom something was created.
    audienceType: URIRef  # The target group associated with a given audience (e.g. veterans, car owners, musicians, etc.).
    audio: URIRef  # An embedded audio object.
    authenticator: URIRef  # The Organization responsible for authenticating the user's subscription. For example, many media apps require a cable/satellite provider to authenticate your subscription before playing media.
    author: URIRef  # The author of this content or rating. Please note that author is special in that HTML 5 provides a special mechanism for indicating authorship via the rel tag. That is equivalent to this and may be used interchangeably.
    availability: URIRef  # The availability of this item&#x2014;for example In stock, Out of stock, Pre-order, etc.
    availabilityEnds: URIRef  # The end of the availability of the product or service included in the offer.
    availabilityStarts: URIRef  # The beginning of the availability of the product or service included in the offer.
    availableAtOrFrom: URIRef  # The place(s) from which the offer can be obtained (e.g. store locations).
    availableChannel: URIRef  # A means of accessing the service (e.g. a phone bank, a web site, a location, etc.).
    availableDeliveryMethod: URIRef  # The delivery method(s) available for this offer.
    availableFrom: URIRef  # When the item is available for pickup from the store, locker, etc.
    availableLanguage: URIRef  # A language someone may use with or at the item, service or place. Please use one of the language codes from the <a href="http://tools.ietf.org/html/bcp47">IETF BCP 47 standard</a>. See also <a class="localLink" href="http://schema.org/inLanguage">inLanguage</a>
    availableOnDevice: URIRef  # Device required to run the application. Used in cases where a specific make/model is required to run the application.
    availableThrough: URIRef  # After this date, the item will no longer be available for pickup.
    award: URIRef  # An award won by or for this item.
    awards: URIRef  # Awards won by or for this item.
    awayTeam: URIRef  # The away team in a sports event.
    baseSalary: URIRef  # The base salary of the job or of an employee in an EmployeeRole.
    bccRecipient: URIRef  # A sub property of recipient. The recipient blind copied on a message.
    bed: URIRef  # The type of bed or beds included in the accommodation. For the single case of just one bed of a certain type, you use bed directly with a text.       If you want to indicate the quantity of a certain kind of bed, use an instance of BedDetails. For more detailed information, use the amenityFeature property.
    beforeMedia: URIRef  # A media object representing the circumstances before performing this direction.
    benefits: URIRef  # Description of benefits associated with the job.
    bestRating: URIRef  # The highest value allowed in this rating system. If bestRating is omitted, 5 is assumed.
    billingAddress: URIRef  # The billing address for the order.
    billingIncrement: URIRef  # This property specifies the minimal quantity and rounding increment that will be the basis for the billing. The unit of measurement is specified by the unitCode property.
    billingPeriod: URIRef  # The time interval used to compute the invoice.
    birthDate: URIRef  # Date of birth.
    birthPlace: URIRef  # The place where the person was born.
    bitrate: URIRef  # The bitrate of the media object.
    blogPost: URIRef  # A posting that is part of this blog.
    blogPosts: URIRef  # The postings that are part of this blog.
    boardingGroup: URIRef  # The airline-specific indicator of boarding order / preference.
    boardingPolicy: URIRef  # The type of boarding policy used by the airline (e.g. zone-based or group-based).
    bookEdition: URIRef  # The edition of the book.
    bookFormat: URIRef  # The format of the book.
    bookingAgent: URIRef  # 'bookingAgent' is an out-dated term indicating a 'broker' that serves as a booking agent.
    bookingTime: URIRef  # The date and time the reservation was booked.
    borrower: URIRef  # A sub property of participant. The person that borrows the object being lent.
    box: URIRef  # A box is the area enclosed by the rectangle formed by two points. The first point is the lower corner, the second point is the upper corner. A box is expressed as two points separated by a space character.
    branchCode: URIRef  # A short textual code (also called "store code") that uniquely identifies a place of business. The code is typically assigned by the parentOrganization and used in structured URLs.<br/><br/>  For example, in the URL http://www.starbucks.co.uk/store-locator/etc/detail/3047 the code "3047" is a branchCode for a particular branch.
    branchOf: URIRef  # The larger organization that this local business is a branch of, if any. Not to be confused with (anatomical)<a class="localLink" href="http://schema.org/branch">branch</a>.
    brand: URIRef  # The brand(s) associated with a product or service, or the brand(s) maintained by an organization or business person.
    breadcrumb: URIRef  # A set of links that can help a user understand and navigate a website hierarchy.
    broadcastAffiliateOf: URIRef  # The media network(s) whose content is broadcast on this station.
    broadcastChannelId: URIRef  # The unique address by which the BroadcastService can be identified in a provider lineup. In US, this is typically a number.
    broadcastDisplayName: URIRef  # The name displayed in the channel guide. For many US affiliates, it is the network name.
    broadcastFrequency: URIRef  # The frequency used for over-the-air broadcasts. Numeric values or simple ranges e.g. 87-99. In addition a shortcut idiom is supported for frequences of AM and FM radio channels, e.g. "87 FM".
    broadcastFrequencyValue: URIRef  # The frequency in MHz for a particular broadcast.
    broadcastOfEvent: URIRef  # The event being broadcast such as a sporting event or awards ceremony.
    broadcastServiceTier: URIRef  # The type of service required to have access to the channel (e.g. Standard or Premium).
    broadcastTimezone: URIRef  # The timezone in <a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601 format</a> for which the service bases its broadcasts
    broadcaster: URIRef  # The organization owning or operating the broadcast service.
    broker: URIRef  # An entity that arranges for an exchange between a buyer and a seller.  In most cases a broker never acquires or releases ownership of a product or service involved in an exchange.  If it is not clear whether an entity is a broker, seller, or buyer, the latter two terms are preferred.
    browserRequirements: URIRef  # Specifies browser requirements in human-readable text. For example, 'requires HTML5 support'.
    busName: URIRef  # The name of the bus (e.g. Bolt Express).
    busNumber: URIRef  # The unique identifier for the bus.
    businessFunction: URIRef  # The business function (e.g. sell, lease, repair, dispose) of the offer or component of a bundle (TypeAndQuantityNode). The default is http://purl.org/goodrelations/v1#Sell.
    buyer: URIRef  # A sub property of participant. The participant/person/organization that bought the object.
    byArtist: URIRef  # The artist that performed this album or recording.
    calories: URIRef  # The number of calories.
    candidate: URIRef  # A sub property of object. The candidate subject of this action.
    caption: URIRef  # The caption for this object. For downloadable machine formats (closed caption, subtitles etc.) use MediaObject and indicate the <a class="localLink" href="http://schema.org/encodingFormat">encodingFormat</a>.
    carbohydrateContent: URIRef  # The number of grams of carbohydrates.
    cargoVolume: URIRef  # The available volume for cargo or luggage. For automobiles, this is usually the trunk volume.<br/><br/>  Typical unit code(s): LTR for liters, FTQ for cubic foot/feet<br/><br/>  Note: You can use <a class="localLink" href="http://schema.org/minValue">minValue</a> and <a class="localLink" href="http://schema.org/maxValue">maxValue</a> to indicate ranges.
    carrier: URIRef  # 'carrier' is an out-dated term indicating the 'provider' for parcel delivery and flights.
    carrierRequirements: URIRef  # Specifies specific carrier(s) requirements for the application (e.g. an application may only work on a specific carrier network).
    catalog: URIRef  # A data catalog which contains this dataset.
    catalogNumber: URIRef  # The catalog number for the release.
    category: URIRef  # A category for the item. Greater signs or slashes can be used to informally indicate a category hierarchy.
    ccRecipient: URIRef  # A sub property of recipient. The recipient copied on a message.
    character: URIRef  # Fictional person connected with a creative work.
    characterAttribute: URIRef  # A piece of data that represents a particular aspect of a fictional character (skill, power, character points, advantage, disadvantage).
    characterName: URIRef  # The name of a character played in some acting or performing role, i.e. in a PerformanceRole.
    cheatCode: URIRef  # Cheat codes to the game.
    checkinTime: URIRef  # The earliest someone may check into a lodging establishment.
    checkoutTime: URIRef  # The latest someone may check out of a lodging establishment.
    childMaxAge: URIRef  # Maximal age of the child.
    childMinAge: URIRef  # Minimal age of the child.
    children: URIRef  # A child of the person.
    cholesterolContent: URIRef  # The number of milligrams of cholesterol.
    circle: URIRef  # A circle is the circular region of a specified radius centered at a specified latitude and longitude. A circle is expressed as a pair followed by a radius in meters.
    citation: URIRef  # A citation or reference to another creative work, such as another publication, web page, scholarly article, etc.
    claimReviewed: URIRef  # A short summary of the specific claims reviewed in a ClaimReview.
    clipNumber: URIRef  # Position of the clip within an ordered group of clips.
    closes: URIRef  # The closing hour of the place or service on the given day(s) of the week.
    coach: URIRef  # A person that acts in a coaching role for a sports team.
    codeRepository: URIRef  # Link to the repository where the un-compiled, human readable code and related code is located (SVN, github, CodePlex).
    codeSampleType: URIRef  # What type of code sample: full (compile ready) solution, code snippet, inline code, scripts, template.
    colleague: URIRef  # A colleague of the person.
    colleagues: URIRef  # A colleague of the person.
    collection: URIRef  # A sub property of object. The collection target of the action.
    color: URIRef  # The color of the product.
    comment: URIRef  # Comments, typically from users.
    commentCount: URIRef  # The number of comments this CreativeWork (e.g. Article, Question or Answer) has received. This is most applicable to works published in Web sites with commenting system; additional comments may exist elsewhere.
    commentText: URIRef  # The text of the UserComment.
    commentTime: URIRef  # The time at which the UserComment was made.
    competitor: URIRef  # A competitor in a sports event.
    composer: URIRef  # The person or organization who wrote a composition, or who is the composer of a work performed at some event.
    confirmationNumber: URIRef  # A number that confirms the given order or payment has been received.
    contactOption: URIRef  # An option available on this contact point (e.g. a toll-free number or support for hearing-impaired callers).
    contactPoint: URIRef  # A contact point for a person or organization.
    contactPoints: URIRef  # A contact point for a person or organization.
    contactType: URIRef  # A person or organization can have different contact points, for different purposes. For example, a sales contact point, a PR contact point and so on. This property is used to specify the kind of contact point.
    containedIn: URIRef  # The basic containment relation between a place and one that contains it.
    containedInPlace: URIRef  # The basic containment relation between a place and one that contains it.
    containsPlace: URIRef  # The basic containment relation between a place and another that it contains.
    containsSeason: URIRef  # A season that is part of the media series.
    contentLocation: URIRef  # The location depicted or described in the content. For example, the location in a photograph or painting.
    contentRating: URIRef  # Official rating of a piece of content&#x2014;for example,'MPAA PG-13'.
    contentSize: URIRef  # File size in (mega/kilo) bytes.
    contentType: URIRef  # The supported content type(s) for an EntryPoint response.
    contentUrl: URIRef  # Actual bytes of the media object, for example the image file or video file.
    contributor: URIRef  # A secondary contributor to the CreativeWork or Event.
    cookTime: URIRef  # The time it takes to actually cook the dish, in <a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601 duration format</a>.
    cookingMethod: URIRef  # The method of cooking, such as Frying, Steaming, ...
    copyrightHolder: URIRef  # The party holding the legal copyright to the CreativeWork.
    copyrightYear: URIRef  # The year during which the claimed copyright for the CreativeWork was first asserted.
    countriesNotSupported: URIRef  # Countries for which the application is not supported. You can also provide the two-letter ISO 3166-1 alpha-2 country code.
    countriesSupported: URIRef  # Countries for which the application is supported. You can also provide the two-letter ISO 3166-1 alpha-2 country code.
    countryOfOrigin: URIRef  # The country of the principal offices of the production company or individual responsible for the movie or program.
    course: URIRef  # A sub property of location. The course where this action was taken.
    courseCode: URIRef  # The identifier for the <a class="localLink" href="http://schema.org/Course">Course</a> used by the course <a class="localLink" href="http://schema.org/provider">provider</a> (e.g. CS101 or 6.001).
    courseMode: URIRef  # The medium or means of delivery of the course instance or the mode of study, either as a text label (e.g. "online", "onsite" or "blended"; "synchronous" or "asynchronous"; "full-time" or "part-time") or as a URL reference to a term from a controlled vocabulary (e.g. https://ceds.ed.gov/element/001311#Asynchronous ).
    coursePrerequisites: URIRef  # Requirements for taking the Course. May be completion of another <a class="localLink" href="http://schema.org/Course">Course</a> or a textual description like "permission of instructor". Requirements may be a pre-requisite competency, referenced using <a class="localLink" href="http://schema.org/AlignmentObject">AlignmentObject</a>.
    coverageEndTime: URIRef  # The time when the live blog will stop covering the Event. Note that coverage may continue after the Event concludes.
    coverageStartTime: URIRef  # The time when the live blog will begin covering the Event. Note that coverage may begin before the Event's start time. The LiveBlogPosting may also be created before coverage begins.
    creator: URIRef  # The creator/author of this CreativeWork. This is the same as the Author property for CreativeWork.
    creditedTo: URIRef  # The group the release is credited to if different than the byArtist. For example, Red and Blue is credited to "Stefani Germanotta Band", but by Lady Gaga.
    cssSelector: URIRef  # A CSS selector, e.g. of a <a class="localLink" href="http://schema.org/SpeakableSpecification">SpeakableSpecification</a> or <a class="localLink" href="http://schema.org/WebPageElement">WebPageElement</a>. In the latter case, multiple matches within a page can constitute a single conceptual "Web page element".
    currenciesAccepted: URIRef  # The currency accepted.<br/><br/>  Use standard formats: <a href="http://en.wikipedia.org/wiki/ISO_4217">ISO 4217 currency format</a> e.g. "USD"; <a href="https://en.wikipedia.org/wiki/List_of_cryptocurrencies">Ticker symbol</a> for cryptocurrencies e.g. "BTC"; well known names for <a href="https://en.wikipedia.org/wiki/Local_exchange_trading_system">Local Exchange Tradings Systems</a> (LETS) and other currency types e.g. "Ithaca HOUR".
    currency: URIRef  # The currency in which the monetary amount is expressed.<br/><br/>  Use standard formats: <a href="http://en.wikipedia.org/wiki/ISO_4217">ISO 4217 currency format</a> e.g. "USD"; <a href="https://en.wikipedia.org/wiki/List_of_cryptocurrencies">Ticker symbol</a> for cryptocurrencies e.g. "BTC"; well known names for <a href="https://en.wikipedia.org/wiki/Local_exchange_trading_system">Local Exchange Tradings Systems</a> (LETS) and other currency types e.g. "Ithaca HOUR".
    customer: URIRef  # Party placing the order or paying the invoice.
    dataFeedElement: URIRef  # An item within in a data feed. Data feeds may have many elements.
    dataset: URIRef  # A dataset contained in this catalog.
    datasetTimeInterval: URIRef  # The range of temporal applicability of a dataset, e.g. for a 2011 census dataset, the year 2011 (in ISO 8601 time interval format).
    dateCreated: URIRef  # The date on which the CreativeWork was created or the item was added to a DataFeed.
    dateDeleted: URIRef  # The datetime the item was removed from the DataFeed.
    dateIssued: URIRef  # The date the ticket was issued.
    dateModified: URIRef  # The date on which the CreativeWork was most recently modified or when the item's entry was modified within a DataFeed.
    datePosted: URIRef  # Publication date of an online listing.
    datePublished: URIRef  # Date of first broadcast/publication.
    dateRead: URIRef  # The date/time at which the message has been read by the recipient if a single recipient exists.
    dateReceived: URIRef  # The date/time the message was received if a single recipient exists.
    dateSent: URIRef  # The date/time at which the message was sent.
    dateVehicleFirstRegistered: URIRef  # The date of the first registration of the vehicle with the respective public authorities.
    dateline: URIRef  # A <a href="https://en.wikipedia.org/wiki/Dateline">dateline</a> is a brief piece of text included in news articles that describes where and when the story was written or filed though the date is often omitted. Sometimes only a placename is provided.<br/><br/>  Structured representations of dateline-related information can also be expressed more explicitly using <a class="localLink" href="http://schema.org/locationCreated">locationCreated</a> (which represents where a work was created e.g. where a news report was written).  For location depicted or described in the content, use <a class="localLink" href="http://schema.org/contentLocation">contentLocation</a>.<br/><br/>  Dateline summaries are oriented more towards human readers than towards automated processing, and can vary substantially. Some examples: "BEIRUT, Lebanon, June 2.", "Paris, France", "December 19, 2017 11:43AM Reporting from Washington", "Beijing/Moscow", "QUEZON CITY, Philippines".
    dayOfWeek: URIRef  # The day of the week for which these opening hours are valid.
    deathDate: URIRef  # Date of death.
    deathPlace: URIRef  # The place where the person died.
    defaultValue: URIRef  # The default value of the input.  For properties that expect a literal, the default is a literal value, for properties that expect an object, it's an ID reference to one of the current values.
    deliveryAddress: URIRef  # Destination address.
    deliveryLeadTime: URIRef  # The typical delay between the receipt of the order and the goods either leaving the warehouse or being prepared for pickup, in case the delivery method is on site pickup.
    deliveryMethod: URIRef  # A sub property of instrument. The method of delivery.
    deliveryStatus: URIRef  # New entry added as the package passes through each leg of its journey (from shipment to final delivery).
    department: URIRef  # A relationship between an organization and a department of that organization, also described as an organization (allowing different urls, logos, opening hours). For example: a store with a pharmacy, or a bakery with a cafe.
    departureAirport: URIRef  # The airport where the flight originates.
    departureBusStop: URIRef  # The stop or station from which the bus departs.
    departureGate: URIRef  # Identifier of the flight's departure gate.
    departurePlatform: URIRef  # The platform from which the train departs.
    departureStation: URIRef  # The station from which the train departs.
    departureTerminal: URIRef  # Identifier of the flight's departure terminal.
    departureTime: URIRef  # The expected departure time.
    dependencies: URIRef  # Prerequisites needed to fulfill steps in article.
    depth: URIRef  # The depth of the item.
    description: URIRef  # A description of the item.
    device: URIRef  # Device required to run the application. Used in cases where a specific make/model is required to run the application.
    director: URIRef  # A director of e.g. tv, radio, movie, video gaming etc. content, or of an event. Directors can be associated with individual items or with a series, episode, clip.
    directors: URIRef  # A director of e.g. tv, radio, movie, video games etc. content. Directors can be associated with individual items or with a series, episode, clip.
    disambiguatingDescription: URIRef  # A sub property of description. A short description of the item used to disambiguate from other, similar items. Information from other properties (in particular, name) may be necessary for the description to be useful for disambiguation.
    discount: URIRef  # Any discount applied (to an Order).
    discountCode: URIRef  # Code used to redeem a discount.
    discountCurrency: URIRef  # The currency of the discount.<br/><br/>  Use standard formats: <a href="http://en.wikipedia.org/wiki/ISO_4217">ISO 4217 currency format</a> e.g. "USD"; <a href="https://en.wikipedia.org/wiki/List_of_cryptocurrencies">Ticker symbol</a> for cryptocurrencies e.g. "BTC"; well known names for <a href="https://en.wikipedia.org/wiki/Local_exchange_trading_system">Local Exchange Tradings Systems</a> (LETS) and other currency types e.g. "Ithaca HOUR".
    discusses: URIRef  # Specifies the CreativeWork associated with the UserComment.
    discussionUrl: URIRef  # A link to the page containing the comments of the CreativeWork.
    dissolutionDate: URIRef  # The date that this organization was dissolved.
    distance: URIRef  # The distance travelled, e.g. exercising or travelling.
    distribution: URIRef  # A downloadable form of this dataset, at a specific location, in a specific format.
    doorTime: URIRef  # The time admission will commence.
    downloadUrl: URIRef  # If the file can be downloaded, URL to download the binary.
    downvoteCount: URIRef  # The number of downvotes this question, answer or comment has received from the community.
    driveWheelConfiguration: URIRef  # The drive wheel configuration, i.e. which roadwheels will receive torque from the vehicle's engine via the drivetrain.
    dropoffLocation: URIRef  # Where a rental car can be dropped off.
    dropoffTime: URIRef  # When a rental car can be dropped off.
    duns: URIRef  # The Dun &amp; Bradstreet DUNS number for identifying an organization or business person.
    duration: URIRef  # The duration of the item (movie, audio recording, event, etc.) in <a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601 date format</a>.
    durationOfWarranty: URIRef  # The duration of the warranty promise. Common unitCode values are ANN for year, MON for months, or DAY for days.
    duringMedia: URIRef  # A media object representing the circumstances while performing this direction.
    editor: URIRef  # Specifies the Person who edited the CreativeWork.
    educationalAlignment: URIRef  # An alignment to an established educational framework.<br/><br/>  This property should not be used where the nature of the alignment can be described using a simple property, for example to express that a resource <a class="localLink" href="http://schema.org/teaches">teaches</a> or <a class="localLink" href="http://schema.org/assesses">assesses</a> a competency.
    educationalCredentialAwarded: URIRef  # A description of the qualification, award, certificate, diploma or other educational credential awarded as a consequence of successful completion of this course or program.
    educationalFramework: URIRef  # The framework to which the resource being described is aligned.
    educationalRole: URIRef  # An educationalRole of an EducationalAudience.
    educationalUse: URIRef  # The purpose of a work in the context of education; for example, 'assignment', 'group work'.
    elevation: URIRef  # The elevation of a location (<a href="https://en.wikipedia.org/wiki/World_Geodetic_System">WGS 84</a>). Values may be of the form 'NUMBER UNIT<em>OF</em>MEASUREMENT' (e.g., '1,000 m', '3,200 ft') while numbers alone should be assumed to be a value in meters.
    eligibleCustomerType: URIRef  # The type(s) of customers for which the given offer is valid.
    eligibleDuration: URIRef  # The duration for which the given offer is valid.
    eligibleQuantity: URIRef  # The interval and unit of measurement of ordering quantities for which the offer or price specification is valid. This allows e.g. specifying that a certain freight charge is valid only for a certain quantity.
    eligibleRegion: URIRef  # The ISO 3166-1 (ISO 3166-1 alpha-2) or ISO 3166-2 code, the place, or the GeoShape for the geo-political region(s) for which the offer or delivery charge specification is valid.<br/><br/>  See also <a class="localLink" href="http://schema.org/ineligibleRegion">ineligibleRegion</a>.
    eligibleTransactionVolume: URIRef  # The transaction volume, in a monetary unit, for which the offer or price specification is valid, e.g. for indicating a minimal purchasing volume, to express free shipping above a certain order volume, or to limit the acceptance of credit cards to purchases to a certain minimal amount.
    email: URIRef  # Email address.
    embedUrl: URIRef  # A URL pointing to a player for a specific video. In general, this is the information in the <code>src</code> element of an <code>embed</code> tag and should not be the same as the content of the <code>loc</code> tag.
    employee: URIRef  # Someone working for this organization.
    employees: URIRef  # People working for this organization.
    employmentType: URIRef  # Type of employment (e.g. full-time, part-time, contract, temporary, seasonal, internship).
    encodesCreativeWork: URIRef  # The CreativeWork encoded by this media object.
    encoding: URIRef  # A media object that encodes this CreativeWork. This property is a synonym for associatedMedia.
    encodingFormat: URIRef  # Media type typically expressed using a MIME format (see <a href="http://www.iana.org/assignments/media-types/media-types.xhtml">IANA site</a> and <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types">MDN reference</a>) e.g. application/zip for a SoftwareApplication binary, audio/mpeg for .mp3 etc.).<br/><br/>  In cases where a <a class="localLink" href="http://schema.org/CreativeWork">CreativeWork</a> has several media type representations, <a class="localLink" href="http://schema.org/encoding">encoding</a> can be used to indicate each <a class="localLink" href="http://schema.org/MediaObject">MediaObject</a> alongside particular <a class="localLink" href="http://schema.org/encodingFormat">encodingFormat</a> information.<br/><br/>  Unregistered or niche encoding and file formats can be indicated instead via the most appropriate URL, e.g. defining Web page or a Wikipedia/Wikidata entry.
    encodingType: URIRef  # The supported encoding type(s) for an EntryPoint request.
    encodings: URIRef  # A media object that encodes this CreativeWork.
    endDate: URIRef  # The end date and time of the item (in <a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601 date format</a>).
    endTime: URIRef  # The endTime of something. For a reserved event or service (e.g. FoodEstablishmentReservation), the time that it is expected to end. For actions that span a period of time, when the action was performed. e.g. John wrote a book from January to <em>December</em>. For media, including audio and video, it's the time offset of the end of a clip within a larger file.<br/><br/>  Note that Event uses startDate/endDate instead of startTime/endTime, even when describing dates with times. This situation may be clarified in future revisions.
    endorsee: URIRef  # A sub property of participant. The person/organization being supported.
    entertainmentBusiness: URIRef  # A sub property of location. The entertainment business where the action occurred.
    episode: URIRef  # An episode of a tv, radio or game media within a series or season.
    episodeNumber: URIRef  # Position of the episode within an ordered group of episodes.
    episodes: URIRef  # An episode of a TV/radio series or season.
    equal: URIRef  # This ordering relation for qualitative values indicates that the subject is equal to the object.
    error: URIRef  # For failed actions, more information on the cause of the failure.
    estimatedCost: URIRef  # The estimated cost of the supply or supplies consumed when performing instructions.
    estimatedFlightDuration: URIRef  # The estimated time the flight will take.
    estimatedSalary: URIRef  # An estimated salary for a job posting or occupation, based on a variety of variables including, but not limited to industry, job title, and location. Estimated salaries  are often computed by outside organizations rather than the hiring organization, who may not have committed to the estimated value.
    event: URIRef  # Upcoming or past event associated with this place, organization, or action.
    eventStatus: URIRef  # An eventStatus of an event represents its status; particularly useful when an event is cancelled or rescheduled.
    events: URIRef  # Upcoming or past events associated with this place or organization.
    exampleOfWork: URIRef  # A creative work that this work is an example/instance/realization/derivation of.
    executableLibraryName: URIRef  # Library file name e.g., mscorlib.dll, system.web.dll.
    exerciseCourse: URIRef  # A sub property of location. The course where this action was taken.
    exifData: URIRef  # exif data for this object.
    expectedArrivalFrom: URIRef  # The earliest date the package may arrive.
    expectedArrivalUntil: URIRef  # The latest date the package may arrive.
    expectsAcceptanceOf: URIRef  # An Offer which must be accepted before the user can perform the Action. For example, the user may need to buy a movie before being able to watch it.
    experienceRequirements: URIRef  # Description of skills and experience needed for the position or Occupation.
    expires: URIRef  # Date the content expires and is no longer useful or available. For example a <a class="localLink" href="http://schema.org/VideoObject">VideoObject</a> or <a class="localLink" href="http://schema.org/NewsArticle">NewsArticle</a> whose availability or relevance is time-limited, or a <a class="localLink" href="http://schema.org/ClaimReview">ClaimReview</a> fact check whose publisher wants to indicate that it may no longer be relevant (or helpful to highlight) after some date.
    familyName: URIRef  # Family name. In the U.S., the last name of an Person. This can be used along with givenName instead of the name property.
    fatContent: URIRef  # The number of grams of fat.
    faxNumber: URIRef  # The fax number.
    featureList: URIRef  # Features or modules provided by this application (and possibly required by other applications).
    feesAndCommissionsSpecification: URIRef  # Description of fees, commissions, and other terms applied either to a class of financial product, or by a financial service organization.
    fiberContent: URIRef  # The number of grams of fiber.
    fileFormat: URIRef  # Media type, typically MIME format (see <a href="http://www.iana.org/assignments/media-types/media-types.xhtml">IANA site</a>) of the content e.g. application/zip of a SoftwareApplication binary. In cases where a CreativeWork has several media type representations, 'encoding' can be used to indicate each MediaObject alongside particular fileFormat information. Unregistered or niche file formats can be indicated instead via the most appropriate URL, e.g. defining Web page or a Wikipedia entry.
    fileSize: URIRef  # Size of the application / package (e.g. 18MB). In the absence of a unit (MB, KB etc.), KB will be assumed.
    firstPerformance: URIRef  # The date and place the work was first performed.
    flightDistance: URIRef  # The distance of the flight.
    flightNumber: URIRef  # The unique identifier for a flight including the airline IATA code. For example, if describing United flight 110, where the IATA code for United is 'UA', the flightNumber is 'UA110'.
    floorSize: URIRef  # The size of the accommodation, e.g. in square meter or squarefoot. Typical unit code(s): MTK for square meter, FTK for square foot, or YDK for square yard
    followee: URIRef  # A sub property of object. The person or organization being followed.
    follows: URIRef  # The most generic uni-directional social relation.
    foodEstablishment: URIRef  # A sub property of location. The specific food establishment where the action occurred.
    foodEvent: URIRef  # A sub property of location. The specific food event where the action occurred.
    founder: URIRef  # A person who founded this organization.
    founders: URIRef  # A person who founded this organization.
    foundingDate: URIRef  # The date that this organization was founded.
    foundingLocation: URIRef  # The place where the Organization was founded.
    free: URIRef  # A flag to signal that the item, event, or place is accessible for free.
    fromLocation: URIRef  # A sub property of location. The original location of the object or the agent before the action.
    fuelConsumption: URIRef  # The amount of fuel consumed for traveling a particular distance or temporal duration with the given vehicle (e.g. liters per 100 km).<br/><br/>  <ul> <li>Note 1: There are unfortunately no standard unit codes for liters per 100 km.  Use <a class="localLink" href="http://schema.org/unitText">unitText</a> to indicate the unit of measurement, e.g. L/100 km.</li> <li>Note 2: There are two ways of indicating the fuel consumption, <a class="localLink" href="http://schema.org/fuelConsumption">fuelConsumption</a> (e.g. 8 liters per 100 km) and <a class="localLink" href="http://schema.org/fuelEfficiency">fuelEfficiency</a> (e.g. 30 miles per gallon). They are reciprocal.</li> <li>Note 3: Often, the absolute value is useful only when related to driving speed ("at 80 km/h") or usage pattern ("city traffic"). You can use <a class="localLink" href="http://schema.org/valueReference">valueReference</a> to link the value for the fuel consumption to another value.</li> </ul>
    fuelEfficiency: URIRef  # The distance traveled per unit of fuel used; most commonly miles per gallon (mpg) or kilometers per liter (km/L).<br/><br/>  <ul> <li>Note 1: There are unfortunately no standard unit codes for miles per gallon or kilometers per liter. Use <a class="localLink" href="http://schema.org/unitText">unitText</a> to indicate the unit of measurement, e.g. mpg or km/L.</li> <li>Note 2: There are two ways of indicating the fuel consumption, <a class="localLink" href="http://schema.org/fuelConsumption">fuelConsumption</a> (e.g. 8 liters per 100 km) and <a class="localLink" href="http://schema.org/fuelEfficiency">fuelEfficiency</a> (e.g. 30 miles per gallon). They are reciprocal.</li> <li>Note 3: Often, the absolute value is useful only when related to driving speed ("at 80 km/h") or usage pattern ("city traffic"). You can use <a class="localLink" href="http://schema.org/valueReference">valueReference</a> to link the value for the fuel economy to another value.</li> </ul>
    fuelType: URIRef  # The type of fuel suitable for the engine or engines of the vehicle. If the vehicle has only one engine, this property can be attached directly to the vehicle.
    funder: URIRef  # A person or organization that supports (sponsors) something through some kind of financial contribution.
    game: URIRef  # Video game which is played on this server.
    gameItem: URIRef  # An item is an object within the game world that can be collected by a player or, occasionally, a non-player character.
    gameLocation: URIRef  # Real or fictional location of the game (or part of game).
    gamePlatform: URIRef  # The electronic systems used to play <a href="http://en.wikipedia.org/wiki/Category:Video_game_platforms">video games</a>.
    gameServer: URIRef  # The server on which  it is possible to play the game.
    gameTip: URIRef  # Links to tips, tactics, etc.
    genre: URIRef  # Genre of the creative work, broadcast channel or group.
    geo: URIRef  # The geo coordinates of the place.
    geoContains: URIRef  # Represents a relationship between two geometries (or the places they represent), relating a containing geometry to a contained geometry. "a contains b iff no points of b lie in the exterior of a, and at least one point of the interior of b lies in the interior of a". As defined in <a href="https://en.wikipedia.org/wiki/DE-9IM">DE-9IM</a>.
    geoCoveredBy: URIRef  # Represents a relationship between two geometries (or the places they represent), relating a geometry to another that covers it. As defined in <a href="https://en.wikipedia.org/wiki/DE-9IM">DE-9IM</a>.
    geoCovers: URIRef  # Represents a relationship between two geometries (or the places they represent), relating a covering geometry to a covered geometry. "Every point of b is a point of (the interior or boundary of) a". As defined in <a href="https://en.wikipedia.org/wiki/DE-9IM">DE-9IM</a>.
    geoCrosses: URIRef  # Represents a relationship between two geometries (or the places they represent), relating a geometry to another that crosses it: "a crosses b: they have some but not all interior points in common, and the dimension of the intersection is less than that of at least one of them". As defined in <a href="https://en.wikipedia.org/wiki/DE-9IM">DE-9IM</a>.
    geoDisjoint: URIRef  # Represents spatial relations in which two geometries (or the places they represent) are topologically disjoint: they have no point in common. They form a set of disconnected geometries." (a symmetric relationship, as defined in <a href="https://en.wikipedia.org/wiki/DE-9IM">DE-9IM</a>)
    geoEquals: URIRef  # Represents spatial relations in which two geometries (or the places they represent) are topologically equal, as defined in <a href="https://en.wikipedia.org/wiki/DE-9IM">DE-9IM</a>. "Two geometries are topologically equal if their interiors intersect and no part of the interior or boundary of one geometry intersects the exterior of the other" (a symmetric relationship)
    geoIntersects: URIRef  # Represents spatial relations in which two geometries (or the places they represent) have at least one point in common. As defined in <a href="https://en.wikipedia.org/wiki/DE-9IM">DE-9IM</a>.
    geoMidpoint: URIRef  # Indicates the GeoCoordinates at the centre of a GeoShape e.g. GeoCircle.
    geoOverlaps: URIRef  # Represents a relationship between two geometries (or the places they represent), relating a geometry to another that geospatially overlaps it, i.e. they have some but not all points in common. As defined in <a href="https://en.wikipedia.org/wiki/DE-9IM">DE-9IM</a>.
    geoRadius: URIRef  # Indicates the approximate radius of a GeoCircle (metres unless indicated otherwise via Distance notation).
    geoTouches: URIRef  # Represents spatial relations in which two geometries (or the places they represent) touch: they have at least one boundary point in common, but no interior points." (a symmetric relationship, as defined in <a href="https://en.wikipedia.org/wiki/DE-9IM">DE-9IM</a> )
    geoWithin: URIRef  # Represents a relationship between two geometries (or the places they represent), relating a geometry to one that contains it, i.e. it is inside (i.e. within) its interior. As defined in <a href="https://en.wikipedia.org/wiki/DE-9IM">DE-9IM</a>.
    geographicArea: URIRef  # The geographic area associated with the audience.
    givenName: URIRef  # Given name. In the U.S., the first name of a Person. This can be used along with familyName instead of the name property.
    globalLocationNumber: URIRef  # The <a href="http://www.gs1.org/gln">Global Location Number</a> (GLN, sometimes also referred to as International Location Number or ILN) of the respective organization, person, or place. The GLN is a 13-digit number used to identify parties and physical locations.
    grantee: URIRef  # The person, organization, contact point, or audience that has been granted this permission.
    greater: URIRef  # This ordering relation for qualitative values indicates that the subject is greater than the object.
    greaterOrEqual: URIRef  # This ordering relation for qualitative values indicates that the subject is greater than or equal to the object.
    gtin12: URIRef  # The GTIN-12 code of the product, or the product to which the offer refers. The GTIN-12 is the 12-digit GS1 Identification Key composed of a U.P.C. Company Prefix, Item Reference, and Check Digit used to identify trade items. See <a href="http://www.gs1.org/barcodes/technical/idkeys/gtin">GS1 GTIN Summary</a> for more details.
    gtin13: URIRef  # The GTIN-13 code of the product, or the product to which the offer refers. This is equivalent to 13-digit ISBN codes and EAN UCC-13. Former 12-digit UPC codes can be converted into a GTIN-13 code by simply adding a preceeding zero. See <a href="http://www.gs1.org/barcodes/technical/idkeys/gtin">GS1 GTIN Summary</a> for more details.
    gtin14: URIRef  # The GTIN-14 code of the product, or the product to which the offer refers. See <a href="http://www.gs1.org/barcodes/technical/idkeys/gtin">GS1 GTIN Summary</a> for more details.
    gtin8: URIRef  # The <a href="http://apps.gs1.org/GDD/glossary/Pages/GTIN-8.aspx">GTIN-8</a> code of the product, or the product to which the offer refers. This code is also known as EAN/UCC-8 or 8-digit EAN. See <a href="http://www.gs1.org/barcodes/technical/idkeys/gtin">GS1 GTIN Summary</a> for more details.
    hasBroadcastChannel: URIRef  # A broadcast channel of a broadcast service.
    hasCourseInstance: URIRef  # An offering of the course at a specific time and place or through specific media or mode of study or to a specific section of students.
    hasDeliveryMethod: URIRef  # Method used for delivery or shipping.
    hasDigitalDocumentPermission: URIRef  # A permission related to the access to this document (e.g. permission to read or write an electronic document). For a public document, specify a grantee with an Audience with audienceType equal to "public".
    hasMap: URIRef  # A URL to a map of the place.
    hasMenu: URIRef  # Either the actual menu as a structured representation, as text, or a URL of the menu.
    hasMenuItem: URIRef  # A food or drink item contained in a menu or menu section.
    hasMenuSection: URIRef  # A subgrouping of the menu (by dishes, course, serving time period, etc.).
    hasOccupation: URIRef  # The Person's occupation. For past professions, use Role for expressing dates.
    hasOfferCatalog: URIRef  # Indicates an OfferCatalog listing for this Organization, Person, or Service.
    hasPOS: URIRef  # Points-of-Sales operated by the organization or person.
    hasPart: URIRef  # Indicates an item or CreativeWork that is part of this item, or CreativeWork (in some sense).
    headline: URIRef  # Headline of the article.
    height: URIRef  # The height of the item.
    highPrice: URIRef  # The highest price of all offers available.<br/><br/>  Usage guidelines:<br/><br/>  <ul> <li>Use values from 0123456789 (Unicode 'DIGIT ZERO' (U+0030) to 'DIGIT NINE' (U+0039)) rather than superficially similiar Unicode symbols.</li> <li>Use '.' (Unicode 'FULL STOP' (U+002E)) rather than ',' to indicate a decimal point. Avoid using these symbols as a readability separator.</li> </ul>
    hiringOrganization: URIRef  # Organization offering the job position.
    homeLocation: URIRef  # A contact location for a person's residence.
    homeTeam: URIRef  # The home team in a sports event.
    honorificPrefix: URIRef  # An honorific prefix preceding a Person's name such as Dr/Mrs/Mr.
    honorificSuffix: URIRef  # An honorific suffix preceding a Person's name such as M.D. /PhD/MSCSW.
    hostingOrganization: URIRef  # The organization (airline, travelers' club, etc.) the membership is made with.
    hoursAvailable: URIRef  # The hours during which this service or contact is available.
    httpMethod: URIRef  # An HTTP method that specifies the appropriate HTTP method for a request to an HTTP EntryPoint. Values are capitalized strings as used in HTTP.
    iataCode: URIRef  # IATA identifier for an airline or airport.
    icaoCode: URIRef  # ICAO identifier for an airport.
    identifier: URIRef  # The identifier property represents any kind of identifier for any kind of <a class="localLink" href="http://schema.org/Thing">Thing</a>, such as ISBNs, GTIN codes, UUIDs etc. Schema.org provides dedicated properties for representing many of these, either as textual strings or as URL (URI) links. See <a href="/docs/datamodel.html#identifierBg">background notes</a> for more details.
    illustrator: URIRef  # The illustrator of the book.
    image: URIRef  # An image of the item. This can be a <a class="localLink" href="http://schema.org/URL">URL</a> or a fully described <a class="localLink" href="http://schema.org/ImageObject">ImageObject</a>.
    inAlbum: URIRef  # The album to which this recording belongs.
    inBroadcastLineup: URIRef  # The CableOrSatelliteService offering the channel.
    inLanguage: URIRef  # The language of the content or performance or used in an action. Please use one of the language codes from the <a href="http://tools.ietf.org/html/bcp47">IETF BCP 47 standard</a>. See also <a class="localLink" href="http://schema.org/availableLanguage">availableLanguage</a>.
    inPlaylist: URIRef  # The playlist to which this recording belongs.
    incentiveCompensation: URIRef  # Description of bonus and commission compensation aspects of the job.
    incentives: URIRef  # Description of bonus and commission compensation aspects of the job.
    includedComposition: URIRef  # Smaller compositions included in this work (e.g. a movement in a symphony).
    includedDataCatalog: URIRef  # A data catalog which contains this dataset (this property was previously 'catalog', preferred name is now 'includedInDataCatalog').
    includedInDataCatalog: URIRef  # A data catalog which contains this dataset.
    includesObject: URIRef  # This links to a node or nodes indicating the exact quantity of the products included in the offer.
    industry: URIRef  # The industry associated with the job position.
    ingredients: URIRef  # A single ingredient used in the recipe, e.g. sugar, flour or garlic.
    installUrl: URIRef  # URL at which the app may be installed, if different from the URL of the item.
    instructor: URIRef  # A person assigned to instruct or provide instructional assistance for the <a class="localLink" href="http://schema.org/CourseInstance">CourseInstance</a>.
    instrument: URIRef  # The object that helped the agent perform the action. e.g. John wrote a book with <em>a pen</em>.
    interactionCount: URIRef  # This property is deprecated, alongside the UserInteraction types on which it depended.
    interactionService: URIRef  # The WebSite or SoftwareApplication where the interactions took place.
    interactionStatistic: URIRef  # The number of interactions for the CreativeWork using the WebSite or SoftwareApplication. The most specific child type of InteractionCounter should be used.
    interactionType: URIRef  # The Action representing the type of interaction. For up votes, +1s, etc. use <a class="localLink" href="http://schema.org/LikeAction">LikeAction</a>. For down votes use <a class="localLink" href="http://schema.org/DislikeAction">DislikeAction</a>. Otherwise, use the most specific Action.
    interactivityType: URIRef  # The predominant mode of learning supported by the learning resource. Acceptable values are 'active', 'expositive', or 'mixed'.
    interestRate: URIRef  # The interest rate, charged or paid, applicable to the financial product. Note: This is different from the calculated annualPercentageRate.
    inventoryLevel: URIRef  # The current approximate inventory level for the item or items.
    isAccessibleForFree: URIRef  # A flag to signal that the item, event, or place is accessible for free.
    isAccessoryOrSparePartFor: URIRef  # A pointer to another product (or multiple products) for which this product is an accessory or spare part.
    isBasedOn: URIRef  # A resource from which this work is derived or from which it is a modification or adaption.
    isBasedOnUrl: URIRef  # A resource that was used in the creation of this resource. This term can be repeated for multiple sources. For example, http://example.com/great-multiplication-intro.html.
    isConsumableFor: URIRef  # A pointer to another product (or multiple products) for which this product is a consumable.
    isFamilyFriendly: URIRef  # Indicates whether this content is family friendly.
    isGift: URIRef  # Was the offer accepted as a gift for someone other than the buyer.
    isLiveBroadcast: URIRef  # True is the broadcast is of a live event.
    isPartOf: URIRef  # Indicates an item or CreativeWork that this item, or CreativeWork (in some sense), is part of.
    isRelatedTo: URIRef  # A pointer to another, somehow related product (or multiple products).
    isSimilarTo: URIRef  # A pointer to another, functionally similar product (or multiple products).
    isVariantOf: URIRef  # A pointer to a base product from which this product is a variant. It is safe to infer that the variant inherits all product features from the base model, unless defined locally. This is not transitive.
    isbn: URIRef  # The ISBN of the book.
    isicV4: URIRef  # The International Standard of Industrial Classification of All Economic Activities (ISIC), Revision 4 code for a particular organization, business person, or place.
    isrcCode: URIRef  # The International Standard Recording Code for the recording.
    issn: URIRef  # The International Standard Serial Number (ISSN) that identifies this serial publication. You can repeat this property to identify different formats of, or the linking ISSN (ISSN-L) for, this serial publication.
    issueNumber: URIRef  # Identifies the issue of publication; for example, "iii" or "2".
    issuedBy: URIRef  # The organization issuing the ticket or permit.
    issuedThrough: URIRef  # The service through with the permit was granted.
    iswcCode: URIRef  # The International Standard Musical Work Code for the composition.
    item: URIRef  # An entity represented by an entry in a list or data feed (e.g. an 'artist' in a list of 'artists')’.
    itemCondition: URIRef  # A predefined value from OfferItemCondition or a textual description of the condition of the product or service, or the products or services included in the offer.
    itemListElement: URIRef  # For itemListElement values, you can use simple strings (e.g. "Peter", "Paul", "Mary"), existing entities, or use ListItem.<br/><br/>  Text values are best if the elements in the list are plain strings. Existing entities are best for a simple, unordered list of existing things in your data. ListItem is used with ordered lists when you want to provide additional context about the element in that list or when the same item might be in different places in different lists.<br/><br/>  Note: The order of elements in your mark-up is not sufficient for indicating the order or elements.  Use ListItem with a 'position' property in such cases.
    itemListOrder: URIRef  # Type of ordering (e.g. Ascending, Descending, Unordered).
    itemOffered: URIRef  # An item being offered (or demanded). The transactional nature of the offer or demand is documented using <a class="localLink" href="http://schema.org/businessFunction">businessFunction</a>, e.g. sell, lease etc. While several common expected types are listed explicitly in this definition, others can be used. Using a second type, such as Product or a subtype of Product, can clarify the nature of the offer.
    itemReviewed: URIRef  # The item that is being reviewed/rated.
    itemShipped: URIRef  # Item(s) being shipped.
    jobBenefits: URIRef  # Description of benefits associated with the job.
    jobLocation: URIRef  # A (typically single) geographic location associated with the job position.
    keywords: URIRef  # Keywords or tags used to describe this content. Multiple entries in a keywords list are typically delimited by commas.
    knownVehicleDamages: URIRef  # A textual description of known damages, both repaired and unrepaired.
    knows: URIRef  # The most generic bi-directional social/work relation.
    landlord: URIRef  # A sub property of participant. The owner of the real estate property.
    language: URIRef  # A sub property of instrument. The language used on this action.
    lastReviewed: URIRef  # Date on which the content on this web page was last reviewed for accuracy and/or completeness.
    latitude: URIRef  # The latitude of a location. For example <code>37.42242</code> (<a href="https://en.wikipedia.org/wiki/World_Geodetic_System">WGS 84</a>).
    learningResourceType: URIRef  # The predominant type or kind characterizing the learning resource. For example, 'presentation', 'handout'.
    legalName: URIRef  # The official name of the organization, e.g. the registered company name.
    leiCode: URIRef  # An organization identifier that uniquely identifies a legal entity as defined in ISO 17442.
    lender: URIRef  # A sub property of participant. The person that lends the object being borrowed.
    lesser: URIRef  # This ordering relation for qualitative values indicates that the subject is lesser than the object.
    lesserOrEqual: URIRef  # This ordering relation for qualitative values indicates that the subject is lesser than or equal to the object.
    license: URIRef  # A license document that applies to this content, typically indicated by URL.
    line: URIRef  # A line is a point-to-point path consisting of two or more points. A line is expressed as a series of two or more point objects separated by space.
    liveBlogUpdate: URIRef  # An update to the LiveBlog.
    loanTerm: URIRef  # The duration of the loan or credit agreement.
    location: URIRef  # The location of for example where the event is happening, an organization is located, or where an action takes place.
    locationCreated: URIRef  # The location where the CreativeWork was created, which may not be the same as the location depicted in the CreativeWork.
    lodgingUnitDescription: URIRef  # A full description of the lodging unit.
    lodgingUnitType: URIRef  # Textual description of the unit type (including suite vs. room, size of bed, etc.).
    logo: URIRef  # An associated logo.
    longitude: URIRef  # The longitude of a location. For example <code>-122.08585</code> (<a href="https://en.wikipedia.org/wiki/World_Geodetic_System">WGS 84</a>).
    loser: URIRef  # A sub property of participant. The loser of the action.
    lowPrice: URIRef  # The lowest price of all offers available.<br/><br/>  Usage guidelines:<br/><br/>  <ul> <li>Use values from 0123456789 (Unicode 'DIGIT ZERO' (U+0030) to 'DIGIT NINE' (U+0039)) rather than superficially similiar Unicode symbols.</li> <li>Use '.' (Unicode 'FULL STOP' (U+002E)) rather than ',' to indicate a decimal point. Avoid using these symbols as a readability separator.</li> </ul>
    lyricist: URIRef  # The person who wrote the words.
    lyrics: URIRef  # The words in the song.
    mainContentOfPage: URIRef  # Indicates if this web page element is the main subject of the page.
    mainEntity: URIRef  # Indicates the primary entity described in some page or other CreativeWork.
    mainEntityOfPage: URIRef  # Indicates a page (or other CreativeWork) for which this thing is the main entity being described. See <a href="/docs/datamodel.html#mainEntityBackground">background notes</a> for details.
    makesOffer: URIRef  # A pointer to products or services offered by the organization or person.
    manufacturer: URIRef  # The manufacturer of the product.
    map: URIRef  # A URL to a map of the place.
    mapType: URIRef  # Indicates the kind of Map, from the MapCategoryType Enumeration.
    maps: URIRef  # A URL to a map of the place.
    material: URIRef  # A material that something is made from, e.g. leather, wool, cotton, paper.
    maxPrice: URIRef  # The highest price if the price is a range.
    maxValue: URIRef  # The upper value of some characteristic or property.
    maximumAttendeeCapacity: URIRef  # The total number of individuals that may attend an event or venue.
    mealService: URIRef  # Description of the meals that will be provided or available for purchase.
    median: URIRef  # The median value.
    member: URIRef  # A member of an Organization or a ProgramMembership. Organizations can be members of organizations; ProgramMembership is typically for individuals.
    memberOf: URIRef  # An Organization (or ProgramMembership) to which this Person or Organization belongs.
    members: URIRef  # A member of this organization.
    membershipNumber: URIRef  # A unique identifier for the membership.
    memoryRequirements: URIRef  # Minimum memory requirements.
    mentions: URIRef  # Indicates that the CreativeWork contains a reference to, but is not necessarily about a concept.
    menu: URIRef  # Either the actual menu as a structured representation, as text, or a URL of the menu.
    menuAddOn: URIRef  # Additional menu item(s) such as a side dish of salad or side order of fries that can be added to this menu item. Additionally it can be a menu section containing allowed add-on menu items for this menu item.
    merchant: URIRef  # 'merchant' is an out-dated term for 'seller'.
    messageAttachment: URIRef  # A CreativeWork attached to the message.
    mileageFromOdometer: URIRef  # The total distance travelled by the particular vehicle since its initial production, as read from its odometer.<br/><br/>  Typical unit code(s): KMT for kilometers, SMI for statute miles
    minPrice: URIRef  # The lowest price if the price is a range.
    minValue: URIRef  # The lower value of some characteristic or property.
    minimumPaymentDue: URIRef  # The minimum payment required at this time.
    model: URIRef  # The model of the product. Use with the URL of a ProductModel or a textual representation of the model identifier. The URL of the ProductModel can be from an external source. It is recommended to additionally provide strong product identifiers via the gtin8/gtin13/gtin14 and mpn properties.
    modifiedTime: URIRef  # The date and time the reservation was modified.
    mpn: URIRef  # The Manufacturer Part Number (MPN) of the product, or the product to which the offer refers.
    multipleValues: URIRef  # Whether multiple values are allowed for the property.  Default is false.
    musicArrangement: URIRef  # An arrangement derived from the composition.
    musicBy: URIRef  # The composer of the soundtrack.
    musicCompositionForm: URIRef  # The type of composition (e.g. overture, sonata, symphony, etc.).
    musicGroupMember: URIRef  # A member of a music group&#x2014;for example, John, Paul, George, or Ringo.
    musicReleaseFormat: URIRef  # Format of this release (the type of recording media used, ie. compact disc, digital media, LP, etc.).
    musicalKey: URIRef  # The key, mode, or scale this composition uses.
    naics: URIRef  # The North American Industry Classification System (NAICS) code for a particular organization or business person.
    name: URIRef  # The name of the item.
    namedPosition: URIRef  # A position played, performed or filled by a person or organization, as part of an organization. For example, an athlete in a SportsTeam might play in the position named 'Quarterback'.
    nationality: URIRef  # Nationality of the person.
    netWorth: URIRef  # The total financial value of the person as calculated by subtracting assets from liabilities.
    nextItem: URIRef  # A link to the ListItem that follows the current one.
    nonEqual: URIRef  # This ordering relation for qualitative values indicates that the subject is not equal to the object.
    numAdults: URIRef  # The number of adults staying in the unit.
    numChildren: URIRef  # The number of children staying in the unit.
    numTracks: URIRef  # The number of tracks in this album or playlist.
    numberOfAirbags: URIRef  # The number or type of airbags in the vehicle.
    numberOfAxles: URIRef  # The number of axles.<br/><br/>  Typical unit code(s): C62
    numberOfBeds: URIRef  # The quantity of the given bed type available in the HotelRoom, Suite, House, or Apartment.
    numberOfDoors: URIRef  # The number of doors.<br/><br/>  Typical unit code(s): C62
    numberOfEmployees: URIRef  # The number of employees in an organization e.g. business.
    numberOfEpisodes: URIRef  # The number of episodes in this season or series.
    numberOfForwardGears: URIRef  # The total number of forward gears available for the transmission system of the vehicle.<br/><br/>  Typical unit code(s): C62
    numberOfItems: URIRef  # The number of items in an ItemList. Note that some descriptions might not fully describe all items in a list (e.g., multi-page pagination); in such cases, the numberOfItems would be for the entire list.
    numberOfPages: URIRef  # The number of pages in the book.
    numberOfPlayers: URIRef  # Indicate how many people can play this game (minimum, maximum, or range).
    numberOfPreviousOwners: URIRef  # The number of owners of the vehicle, including the current one.<br/><br/>  Typical unit code(s): C62
    numberOfRooms: URIRef  # The number of rooms (excluding bathrooms and closets) of the accommodation or lodging business. Typical unit code(s): ROM for room or C62 for no unit. The type of room can be put in the unitText property of the QuantitativeValue.
    numberOfSeasons: URIRef  # The number of seasons in this series.
    numberedPosition: URIRef  # A number associated with a role in an organization, for example, the number on an athlete's jersey.
    nutrition: URIRef  # Nutrition information about the recipe or menu item.
    object: URIRef  # The object upon which the action is carried out, whose state is kept intact or changed. Also known as the semantic roles patient, affected or undergoer (which change their state) or theme (which doesn't). e.g. John read <em>a book</em>.
    occupancy: URIRef  # The allowed total occupancy for the accommodation in persons (including infants etc). For individual accommodations, this is not necessarily the legal maximum but defines the permitted usage as per the contractual agreement (e.g. a double room used by a single person). Typical unit code(s): C62 for person
    occupationLocation: URIRef  # The region/country for which this occupational description is appropriate. Note that educational requirements and qualifications can vary between jurisdictions.
    offerCount: URIRef  # The number of offers for the product.
    offeredBy: URIRef  # A pointer to the organization or person making the offer.
    offers: URIRef  # An offer to provide this item&#x2014;for example, an offer to sell a product, rent the DVD of a movie, perform a service, or give away tickets to an event. Use <a class="localLink" href="http://schema.org/businessFunction">businessFunction</a> to indicate the kind of transaction offered, i.e. sell, lease, etc. This property can also be used to describe a <a class="localLink" href="http://schema.org/Demand">Demand</a>. While this property is listed as expected on a number of common types, it can be used in others. In that case, using a second type, such as Product or a subtype of Product, can clarify the nature of the offer.
    openingHours: URIRef  # The general opening hours for a business. Opening hours can be specified as a weekly time range, starting with days, then times per day. Multiple days can be listed with commas ',' separating each day. Day or time ranges are specified using a hyphen '-'.<br/><br/>  <ul> <li>Days are specified using the following two-letter combinations: <code>Mo</code>, <code>Tu</code>, <code>We</code>, <code>Th</code>, <code>Fr</code>, <code>Sa</code>, <code>Su</code>.</li> <li>Times are specified using 24:00 time. For example, 3pm is specified as <code>15:00</code>. </li> <li>Here is an example: <code>&lt;time itemprop="openingHours" datetime=&quot;Tu,Th 16:00-20:00&quot;&gt;Tuesdays and Thursdays 4-8pm&lt;/time&gt;</code>.</li> <li>If a business is open 7 days a week, then it can be specified as <code>&lt;time itemprop=&quot;openingHours&quot; datetime=&quot;Mo-Su&quot;&gt;Monday through Sunday, all day&lt;/time&gt;</code>.</li> </ul>
    openingHoursSpecification: URIRef  # The opening hours of a certain place.
    opens: URIRef  # The opening hour of the place or service on the given day(s) of the week.
    operatingSystem: URIRef  # Operating systems supported (Windows 7, OSX 10.6, Android 1.6).
    opponent: URIRef  # A sub property of participant. The opponent on this action.
    option: URIRef  # A sub property of object. The options subject to this action.
    orderDate: URIRef  # Date order was placed.
    orderDelivery: URIRef  # The delivery of the parcel related to this order or order item.
    orderItemNumber: URIRef  # The identifier of the order item.
    orderItemStatus: URIRef  # The current status of the order item.
    orderNumber: URIRef  # The identifier of the transaction.
    orderQuantity: URIRef  # The number of the item ordered. If the property is not set, assume the quantity is one.
    orderStatus: URIRef  # The current status of the order.
    orderedItem: URIRef  # The item ordered.
    organizer: URIRef  # An organizer of an Event.
    originAddress: URIRef  # Shipper's address.
    ownedFrom: URIRef  # The date and time of obtaining the product.
    ownedThrough: URIRef  # The date and time of giving up ownership on the product.
    owns: URIRef  # Products owned by the organization or person.
    pageEnd: URIRef  # The page on which the work ends; for example "138" or "xvi".
    pageStart: URIRef  # The page on which the work starts; for example "135" or "xiii".
    pagination: URIRef  # Any description of pages that is not separated into pageStart and pageEnd; for example, "1-6, 9, 55" or "10-12, 46-49".
    parent: URIRef  # A parent of this person.
    parentItem: URIRef  # The parent of a question, answer or item in general.
    parentOrganization: URIRef  # The larger organization that this organization is a <a class="localLink" href="http://schema.org/subOrganization">subOrganization</a> of, if any.
    parentService: URIRef  # A broadcast service to which the broadcast service may belong to such as regional variations of a national channel.
    parents: URIRef  # A parents of the person.
    partOfEpisode: URIRef  # The episode to which this clip belongs.
    partOfInvoice: URIRef  # The order is being paid as part of the referenced Invoice.
    partOfOrder: URIRef  # The overall order the items in this delivery were included in.
    partOfSeason: URIRef  # The season to which this episode belongs.
    partOfSeries: URIRef  # The series to which this episode or season belongs.
    partOfTVSeries: URIRef  # The TV series to which this episode or season belongs.
    participant: URIRef  # Other co-agents that participated in the action indirectly. e.g. John wrote a book with <em>Steve</em>.
    partySize: URIRef  # Number of people the reservation should accommodate.
    passengerPriorityStatus: URIRef  # The priority status assigned to a passenger for security or boarding (e.g. FastTrack or Priority).
    passengerSequenceNumber: URIRef  # The passenger's sequence number as assigned by the airline.
    paymentAccepted: URIRef  # Cash, Credit Card, Cryptocurrency, Local Exchange Tradings System, etc.
    paymentDue: URIRef  # The date that payment is due.
    paymentDueDate: URIRef  # The date that payment is due.
    paymentMethod: URIRef  # The name of the credit card or other method of payment for the order.
    paymentMethodId: URIRef  # An identifier for the method of payment used (e.g. the last 4 digits of the credit card).
    paymentStatus: URIRef  # The status of payment; whether the invoice has been paid or not.
    paymentUrl: URIRef  # The URL for sending a payment.
    percentile10: URIRef  # The 10th percentile value.
    percentile25: URIRef  # The 25th percentile value.
    percentile75: URIRef  # The 75th percentile value.
    percentile90: URIRef  # The 90th percentile value.
    performTime: URIRef  # The length of time it takes to perform instructions or a direction (not including time to prepare the supplies), in <a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601 duration format</a>.
    performer: URIRef  # A performer at the event&#x2014;for example, a presenter, musician, musical group or actor.
    performerIn: URIRef  # Event that this person is a performer or participant in.
    performers: URIRef  # The main performer or performers of the event&#x2014;for example, a presenter, musician, or actor.
    permissionType: URIRef  # The type of permission granted the person, organization, or audience.
    permissions: URIRef  # Permission(s) required to run the app (for example, a mobile app may require full internet access or may run only on wifi).
    permitAudience: URIRef  # The target audience for this permit.
    permittedUsage: URIRef  # Indications regarding the permitted usage of the accommodation.
    petsAllowed: URIRef  # Indicates whether pets are allowed to enter the accommodation or lodging business. More detailed information can be put in a text value.
    photo: URIRef  # A photograph of this place.
    photos: URIRef  # Photographs of this place.
    pickupLocation: URIRef  # Where a taxi will pick up a passenger or a rental car can be picked up.
    pickupTime: URIRef  # When a taxi will pickup a passenger or a rental car can be picked up.
    playMode: URIRef  # Indicates whether this game is multi-player, co-op or single-player.  The game can be marked as multi-player, co-op and single-player at the same time.
    playerType: URIRef  # Player type required&#x2014;for example, Flash or Silverlight.
    playersOnline: URIRef  # Number of players on the server.
    polygon: URIRef  # A polygon is the area enclosed by a point-to-point path for which the starting and ending points are the same. A polygon is expressed as a series of four or more space delimited points where the first and final points are identical.
    position: URIRef  # The position of an item in a series or sequence of items.
    postOfficeBoxNumber: URIRef  # The post office box number for PO box addresses.
    postalCode: URIRef  # The postal code. For example, 94043.
    potentialAction: URIRef  # Indicates a potential Action, which describes an idealized action in which this thing would play an 'object' role.
    predecessorOf: URIRef  # A pointer from a previous, often discontinued variant of the product to its newer variant.
    prepTime: URIRef  # The length of time it takes to prepare the items to be used in instructions or a direction, in <a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601 duration format</a>.
    previousItem: URIRef  # A link to the ListItem that preceeds the current one.
    previousStartDate: URIRef  # Used in conjunction with eventStatus for rescheduled or cancelled events. This property contains the previously scheduled start date. For rescheduled events, the startDate property should be used for the newly scheduled start date. In the (rare) case of an event that has been postponed and rescheduled multiple times, this field may be repeated.
    price: URIRef  # The offer price of a product, or of a price component when attached to PriceSpecification and its subtypes.<br/><br/>  Usage guidelines:<br/><br/>  <ul> <li>Use the <a class="localLink" href="http://schema.org/priceCurrency">priceCurrency</a> property (with standard formats: <a href="http://en.wikipedia.org/wiki/ISO_4217">ISO 4217 currency format</a> e.g. "USD"; <a href="https://en.wikipedia.org/wiki/List_of_cryptocurrencies">Ticker symbol</a> for cryptocurrencies e.g. "BTC"; well known names for <a href="https://en.wikipedia.org/wiki/Local_exchange_trading_system">Local Exchange Tradings Systems</a> (LETS) and other currency types e.g. "Ithaca HOUR") instead of including <a href="http://en.wikipedia.org/wiki/Dollar_sign#Currencies_that_use_the_dollar_or_peso_sign">ambiguous symbols</a> such as '$' in the value.</li> <li>Use '.' (Unicode 'FULL STOP' (U+002E)) rather than ',' to indicate a decimal point. Avoid using these symbols as a readability separator.</li> <li>Note that both <a href="http://www.w3.org/TR/xhtml-rdfa-primer/#using-the-content-attribute">RDFa</a> and Microdata syntax allow the use of a "content=" attribute for publishing simple machine-readable values alongside more human-friendly formatting.</li> <li>Use values from 0123456789 (Unicode 'DIGIT ZERO' (U+0030) to 'DIGIT NINE' (U+0039)) rather than superficially similiar Unicode symbols.</li> </ul>
    priceComponent: URIRef  # This property links to all <a class="localLink" href="http://schema.org/UnitPriceSpecification">UnitPriceSpecification</a> nodes that apply in parallel for the <a class="localLink" href="http://schema.org/CompoundPriceSpecification">CompoundPriceSpecification</a> node.
    priceCurrency: URIRef  # The currency of the price, or a price component when attached to <a class="localLink" href="http://schema.org/PriceSpecification">PriceSpecification</a> and its subtypes.<br/><br/>  Use standard formats: <a href="http://en.wikipedia.org/wiki/ISO_4217">ISO 4217 currency format</a> e.g. "USD"; <a href="https://en.wikipedia.org/wiki/List_of_cryptocurrencies">Ticker symbol</a> for cryptocurrencies e.g. "BTC"; well known names for <a href="https://en.wikipedia.org/wiki/Local_exchange_trading_system">Local Exchange Tradings Systems</a> (LETS) and other currency types e.g. "Ithaca HOUR".
    priceRange: URIRef  # The price range of the business, for example <code>$$$</code>.
    priceSpecification: URIRef  # One or more detailed price specifications, indicating the unit price and delivery or payment charges.
    priceType: URIRef  # A short text or acronym indicating multiple price specifications for the same offer, e.g. SRP for the suggested retail price or INVOICE for the invoice price, mostly used in the car industry.
    priceValidUntil: URIRef  # The date after which the price is no longer available.
    primaryImageOfPage: URIRef  # Indicates the main image on the page.
    printColumn: URIRef  # The number of the column in which the NewsArticle appears in the print edition.
    printEdition: URIRef  # The edition of the print product in which the NewsArticle appears.
    printPage: URIRef  # If this NewsArticle appears in print, this field indicates the name of the page on which the article is found. Please note that this field is intended for the exact page name (e.g. A5, B18).
    printSection: URIRef  # If this NewsArticle appears in print, this field indicates the print section in which the article appeared.
    processingTime: URIRef  # Estimated processing time for the service using this channel.
    processorRequirements: URIRef  # Processor architecture required to run the application (e.g. IA64).
    producer: URIRef  # The person or organization who produced the work (e.g. music album, movie, tv/radio series etc.).
    produces: URIRef  # The tangible thing generated by the service, e.g. a passport, permit, etc.
    productID: URIRef  # The product identifier, such as ISBN. For example: <code>meta itemprop="productID" content="isbn:123-456-789"</code>.
    productSupported: URIRef  # The product or service this support contact point is related to (such as product support for a particular product line). This can be a specific product or product line (e.g. "iPhone") or a general category of products or services (e.g. "smartphones").
    productionCompany: URIRef  # The production company or studio responsible for the item e.g. series, video game, episode etc.
    productionDate: URIRef  # The date of production of the item, e.g. vehicle.
    proficiencyLevel: URIRef  # Proficiency needed for this content; expected values: 'Beginner', 'Expert'.
    programMembershipUsed: URIRef  # Any membership in a frequent flyer, hotel loyalty program, etc. being applied to the reservation.
    programName: URIRef  # The program providing the membership.
    programmingLanguage: URIRef  # The computer programming language.
    programmingModel: URIRef  # Indicates whether API is managed or unmanaged.
    propertyID: URIRef  # A commonly used identifier for the characteristic represented by the property, e.g. a manufacturer or a standard code for a property. propertyID can be (1) a prefixed string, mainly meant to be used with standards for product properties; (2) a site-specific, non-prefixed string (e.g. the primary key of the property or the vendor-specific id of the property), or (3) a URL indicating the type of the property, either pointing to an external vocabulary, or a Web resource that describes the property (e.g. a glossary entry). Standards bodies should promote a standard prefix for the identifiers of properties from their standards.
    proteinContent: URIRef  # The number of grams of protein.
    provider: URIRef  # The service provider, service operator, or service performer; the goods producer. Another party (a seller) may offer those services or goods on behalf of the provider. A provider may also serve as the seller.
    providerMobility: URIRef  # Indicates the mobility of a provided service (e.g. 'static', 'dynamic').
    providesBroadcastService: URIRef  # The BroadcastService offered on this channel.
    providesService: URIRef  # The service provided by this channel.
    publicAccess: URIRef  # A flag to signal that the <a class="localLink" href="http://schema.org/Place">Place</a> is open to public visitors.  If this property is omitted there is no assumed default boolean value
    publication: URIRef  # A publication event associated with the item.
    publishedOn: URIRef  # A broadcast service associated with the publication event.
    publisher: URIRef  # The publisher of the creative work.
    publishingPrinciples: URIRef  # The publishingPrinciples property indicates (typically via <a class="localLink" href="http://schema.org/URL">URL</a>) a document describing the editorial principles of an <a class="localLink" href="http://schema.org/Organization">Organization</a> (or individual e.g. a <a class="localLink" href="http://schema.org/Person">Person</a> writing a blog) that relate to their activities as a publisher, e.g. ethics or diversity policies. When applied to a <a class="localLink" href="http://schema.org/CreativeWork">CreativeWork</a> (e.g. <a class="localLink" href="http://schema.org/NewsArticle">NewsArticle</a>) the principles are those of the party primarily responsible for the creation of the <a class="localLink" href="http://schema.org/CreativeWork">CreativeWork</a>.<br/><br/>  While such policies are most typically expressed in natural language, sometimes related information (e.g. indicating a <a class="localLink" href="http://schema.org/funder">funder</a>) can be expressed using schema.org terminology.
    purchaseDate: URIRef  # The date the item e.g. vehicle was purchased by the current owner.
    query: URIRef  # A sub property of instrument. The query used on this action.
    quest: URIRef  # The task that a player-controlled character, or group of characters may complete in order to gain a reward.
    question: URIRef  # A sub property of object. A question.
    ratingCount: URIRef  # The count of total number of ratings.
    ratingValue: URIRef  # The rating for the content.<br/><br/>  Usage guidelines:<br/><br/>  <ul> <li>Use values from 0123456789 (Unicode 'DIGIT ZERO' (U+0030) to 'DIGIT NINE' (U+0039)) rather than superficially similiar Unicode symbols.</li> <li>Use '.' (Unicode 'FULL STOP' (U+002E)) rather than ',' to indicate a decimal point. Avoid using these symbols as a readability separator.</li> </ul>
    readonlyValue: URIRef  # Whether or not a property is mutable.  Default is false. Specifying this for a property that also has a value makes it act similar to a "hidden" input in an HTML form.
    realEstateAgent: URIRef  # A sub property of participant. The real estate agent involved in the action.
    recipe: URIRef  # A sub property of instrument. The recipe/instructions used to perform the action.
    recipeCategory: URIRef  # The category of the recipe—for example, appetizer, entree, etc.
    recipeCuisine: URIRef  # The cuisine of the recipe (for example, French or Ethiopian).
    recipeIngredient: URIRef  # A single ingredient used in the recipe, e.g. sugar, flour or garlic.
    recipeInstructions: URIRef  # A step in making the recipe, in the form of a single item (document, video, etc.) or an ordered list with HowToStep and/or HowToSection items.
    recipeYield: URIRef  # The quantity produced by the recipe (for example, number of people served, number of servings, etc).
    recipient: URIRef  # A sub property of participant. The participant who is at the receiving end of the action.
    recordLabel: URIRef  # The label that issued the release.
    recordedAs: URIRef  # An audio recording of the work.
    recordedAt: URIRef  # The Event where the CreativeWork was recorded. The CreativeWork may capture all or part of the event.
    recordedIn: URIRef  # The CreativeWork that captured all or part of this Event.
    recordingOf: URIRef  # The composition this track is a recording of.
    referenceQuantity: URIRef  # The reference quantity for which a certain price applies, e.g. 1 EUR per 4 kWh of electricity. This property is a replacement for unitOfMeasurement for the advanced cases where the price does not relate to a standard unit.
    referencesOrder: URIRef  # The Order(s) related to this Invoice. One or more Orders may be combined into a single Invoice.
    regionsAllowed: URIRef  # The regions where the media is allowed. If not specified, then it's assumed to be allowed everywhere. Specify the countries in <a href="http://en.wikipedia.org/wiki/ISO_3166">ISO 3166 format</a>.
    relatedLink: URIRef  # A link related to this web page, for example to other related web pages.
    relatedTo: URIRef  # The most generic familial relation.
    releaseDate: URIRef  # The release date of a product or product model. This can be used to distinguish the exact variant of a product.
    releaseNotes: URIRef  # Description of what changed in this version.
    releaseOf: URIRef  # The album this is a release of.
    releasedEvent: URIRef  # The place and time the release was issued, expressed as a PublicationEvent.
    relevantOccupation: URIRef  # The Occupation for the JobPosting.
    remainingAttendeeCapacity: URIRef  # The number of attendee places for an event that remain unallocated.
    replacee: URIRef  # A sub property of object. The object that is being replaced.
    replacer: URIRef  # A sub property of object. The object that replaces.
    replyToUrl: URIRef  # The URL at which a reply may be posted to the specified UserComment.
    reportNumber: URIRef  # The number or other unique designator assigned to a Report by the publishing organization.
    representativeOfPage: URIRef  # Indicates whether this image is representative of the content of the page.
    requiredCollateral: URIRef  # Assets required to secure loan or credit repayments. It may take form of third party pledge, goods, financial instruments (cash, securities, etc.)
    requiredGender: URIRef  # Audiences defined by a person's gender.
    requiredMaxAge: URIRef  # Audiences defined by a person's maximum age.
    requiredMinAge: URIRef  # Audiences defined by a person's minimum age.
    requiredQuantity: URIRef  # The required quantity of the item(s).
    requirements: URIRef  # Component dependency requirements for application. This includes runtime environments and shared libraries that are not included in the application distribution package, but required to run the application (Examples: DirectX, Java or .NET runtime).
    requiresSubscription: URIRef  # Indicates if use of the media require a subscription  (either paid or free). Allowed values are <code>true</code> or <code>false</code> (note that an earlier version had 'yes', 'no').
    reservationFor: URIRef  # The thing -- flight, event, restaurant,etc. being reserved.
    reservationId: URIRef  # A unique identifier for the reservation.
    reservationStatus: URIRef  # The current status of the reservation.
    reservedTicket: URIRef  # A ticket associated with the reservation.
    responsibilities: URIRef  # Responsibilities associated with this role or Occupation.
    result: URIRef  # The result produced in the action. e.g. John wrote <em>a book</em>.
    resultComment: URIRef  # A sub property of result. The Comment created or sent as a result of this action.
    resultReview: URIRef  # A sub property of result. The review that resulted in the performing of the action.
    review: URIRef  # A review of the item.
    reviewAspect: URIRef  # This Review or Rating is relevant to this part or facet of the itemReviewed.
    reviewBody: URIRef  # The actual body of the review.
    reviewCount: URIRef  # The count of total number of reviews.
    reviewRating: URIRef  # The rating given in this review. Note that reviews can themselves be rated. The <code>reviewRating</code> applies to rating given by the review. The <a class="localLink" href="http://schema.org/aggregateRating">aggregateRating</a> property applies to the review itself, as a creative work.
    reviewedBy: URIRef  # People or organizations that have reviewed the content on this web page for accuracy and/or completeness.
    reviews: URIRef  # Review of the item.
    roleName: URIRef  # A role played, performed or filled by a person or organization. For example, the team of creators for a comic book might fill the roles named 'inker', 'penciller', and 'letterer'; or an athlete in a SportsTeam might play in the position named 'Quarterback'.
    rsvpResponse: URIRef  # The response (yes, no, maybe) to the RSVP.
    runtime: URIRef  # Runtime platform or script interpreter dependencies (Example - Java v1, Python2.3, .Net Framework 3.0).
    runtimePlatform: URIRef  # Runtime platform or script interpreter dependencies (Example - Java v1, Python2.3, .Net Framework 3.0).
    salaryCurrency: URIRef  # The currency (coded using <a href="http://en.wikipedia.org/wiki/ISO_4217">ISO 4217</a> ) used for the main salary information in this job posting or for this employee.
    sameAs: URIRef  # URL of a reference Web page that unambiguously indicates the item's identity. E.g. the URL of the item's Wikipedia page, Wikidata entry, or official website.
    sampleType: URIRef  # What type of code sample: full (compile ready) solution, code snippet, inline code, scripts, template.
    saturatedFatContent: URIRef  # The number of grams of saturated fat.
    scheduledPaymentDate: URIRef  # The date the invoice is scheduled to be paid.
    scheduledTime: URIRef  # The time the object is scheduled to.
    schemaVersion: URIRef  # Indicates (by URL or string) a particular version of a schema used in some CreativeWork. For example, a document could declare a schemaVersion using an URL such as http://schema.org/version/2.0/ if precise indication of schema version was required by some application.
    screenCount: URIRef  # The number of screens in the movie theater.
    screenshot: URIRef  # A link to a screenshot image of the app.
    season: URIRef  # A season in a media series.
    seasonNumber: URIRef  # Position of the season within an ordered group of seasons.
    seasons: URIRef  # A season in a media series.
    seatNumber: URIRef  # The location of the reserved seat (e.g., 27).
    seatRow: URIRef  # The row location of the reserved seat (e.g., B).
    seatSection: URIRef  # The section location of the reserved seat (e.g. Orchestra).
    seatingType: URIRef  # The type/class of the seat.
    securityScreening: URIRef  # The type of security screening the passenger is subject to.
    seeks: URIRef  # A pointer to products or services sought by the organization or person (demand).
    seller: URIRef  # An entity which offers (sells / leases / lends / loans) the services / goods.  A seller may also be a provider.
    sender: URIRef  # A sub property of participant. The participant who is at the sending end of the action.
    serialNumber: URIRef  # The serial number or any alphanumeric identifier of a particular product. When attached to an offer, it is a shortcut for the serial number of the product included in the offer.
    serverStatus: URIRef  # Status of a game server.
    servesCuisine: URIRef  # The cuisine of the restaurant.
    serviceArea: URIRef  # The geographic area where the service is provided.
    serviceAudience: URIRef  # The audience eligible for this service.
    serviceLocation: URIRef  # The location (e.g. civic structure, local business, etc.) where a person can go to access the service.
    serviceOperator: URIRef  # The operating organization, if different from the provider.  This enables the representation of services that are provided by an organization, but operated by another organization like a subcontractor.
    serviceOutput: URIRef  # The tangible thing generated by the service, e.g. a passport, permit, etc.
    servicePhone: URIRef  # The phone number to use to access the service.
    servicePostalAddress: URIRef  # The address for accessing the service by mail.
    serviceSmsNumber: URIRef  # The number to access the service by text message.
    serviceType: URIRef  # The type of service being offered, e.g. veterans' benefits, emergency relief, etc.
    serviceUrl: URIRef  # The website to access the service.
    servingSize: URIRef  # The serving size, in terms of the number of volume or mass.
    sharedContent: URIRef  # A CreativeWork such as an image, video, or audio clip shared as part of this posting.
    sibling: URIRef  # A sibling of the person.
    siblings: URIRef  # A sibling of the person.
    significantLink: URIRef  # One of the more significant URLs on the page. Typically, these are the non-navigation links that are clicked on the most.
    significantLinks: URIRef  # The most significant URLs on the page. Typically, these are the non-navigation links that are clicked on the most.
    skills: URIRef  # A statement of knowledge, skill, ability, task or any other assertion expressing a competency that is desired or required to fulfill this role or to work in this occupation.
    sku: URIRef  # The Stock Keeping Unit (SKU), i.e. a merchant-specific identifier for a product or service, or the product to which the offer refers.
    slogan: URIRef  # A slogan or motto associated with the item.
    smokingAllowed: URIRef  # Indicates whether it is allowed to smoke in the place, e.g. in the restaurant, hotel or hotel room.
    sodiumContent: URIRef  # The number of milligrams of sodium.
    softwareAddOn: URIRef  # Additional content for a software application.
    softwareHelp: URIRef  # Software application help.
    softwareRequirements: URIRef  # Component dependency requirements for application. This includes runtime environments and shared libraries that are not included in the application distribution package, but required to run the application (Examples: DirectX, Java or .NET runtime).
    softwareVersion: URIRef  # Version of the software instance.
    sourceOrganization: URIRef  # The Organization on whose behalf the creator was working.
    spatial: URIRef  # The "spatial" property can be used in cases when more specific properties (e.g. <a class="localLink" href="http://schema.org/locationCreated">locationCreated</a>, <a class="localLink" href="http://schema.org/spatialCoverage">spatialCoverage</a>, <a class="localLink" href="http://schema.org/contentLocation">contentLocation</a>) are not known to be appropriate.
    spatialCoverage: URIRef  # The spatialCoverage of a CreativeWork indicates the place(s) which are the focus of the content. It is a subproperty of       contentLocation intended primarily for more technical and detailed materials. For example with a Dataset, it indicates       areas that the dataset describes: a dataset of New York weather would have spatialCoverage which was the place: the state of New York.
    speakable: URIRef  # Indicates sections of a Web page that are particularly 'speakable' in the sense of being highlighted as being especially appropriate for text-to-speech conversion. Other sections of a page may also be usefully spoken in particular circumstances; the 'speakable' property serves to indicate the parts most likely to be generally useful for speech.<br/><br/>  The <em>speakable</em> property can be repeated an arbitrary number of times, with three kinds of possible 'content-locator' values:<br/><br/>  1.) <em>id-value</em> URL references - uses <em>id-value</em> of an element in the page being annotated. The simplest use of <em>speakable</em> has (potentially relative) URL values, referencing identified sections of the document concerned.<br/><br/>  2.) CSS Selectors - addresses content in the annotated page, eg. via class attribute. Use the <a class="localLink" href="http://schema.org/cssSelector">cssSelector</a> property.<br/><br/>  3.)  XPaths - addresses content via XPaths (assuming an XML view of the content). Use the <a class="localLink" href="http://schema.org/xpath">xpath</a> property.<br/><br/>  For more sophisticated markup of speakable sections beyond simple ID references, either CSS selectors or XPath expressions to pick out document section(s) as speakable. For this we define a supporting type, <a class="localLink" href="http://schema.org/SpeakableSpecification">SpeakableSpecification</a>  which is defined to be a possible value of the <em>speakable</em> property.
    specialCommitments: URIRef  # Any special commitments associated with this job posting. Valid entries include VeteranCommit, MilitarySpouseCommit, etc.
    specialOpeningHoursSpecification: URIRef  # The special opening hours of a certain place.<br/><br/>  Use this to explicitly override general opening hours brought in scope by <a class="localLink" href="http://schema.org/openingHoursSpecification">openingHoursSpecification</a> or <a class="localLink" href="http://schema.org/openingHours">openingHours</a>.
    specialty: URIRef  # One of the domain specialities to which this web page's content applies.
    sponsor: URIRef  # A person or organization that supports a thing through a pledge, promise, or financial contribution. e.g. a sponsor of a Medical Study or a corporate sponsor of an event.
    sportsActivityLocation: URIRef  # A sub property of location. The sports activity location where this action occurred.
    sportsEvent: URIRef  # A sub property of location. The sports event where this action occurred.
    sportsTeam: URIRef  # A sub property of participant. The sports team that participated on this action.
    spouse: URIRef  # The person's spouse.
    starRating: URIRef  # An official rating for a lodging business or food establishment, e.g. from national associations or standards bodies. Use the author property to indicate the rating organization, e.g. as an Organization with name such as (e.g. HOTREC, DEHOGA, WHR, or Hotelstars).
    startDate: URIRef  # The start date and time of the item (in <a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601 date format</a>).
    startTime: URIRef  # The startTime of something. For a reserved event or service (e.g. FoodEstablishmentReservation), the time that it is expected to start. For actions that span a period of time, when the action was performed. e.g. John wrote a book from <em>January</em> to December. For media, including audio and video, it's the time offset of the start of a clip within a larger file.<br/><br/>  Note that Event uses startDate/endDate instead of startTime/endTime, even when describing dates with times. This situation may be clarified in future revisions.
    steeringPosition: URIRef  # The position of the steering wheel or similar device (mostly for cars).
    step: URIRef  # A single step item (as HowToStep, text, document, video, etc.) or a HowToSection.
    stepValue: URIRef  # The stepValue attribute indicates the granularity that is expected (and required) of the value in a PropertyValueSpecification.
    steps: URIRef  # A single step item (as HowToStep, text, document, video, etc.) or a HowToSection (originally misnamed 'steps'; 'step' is preferred).
    storageRequirements: URIRef  # Storage requirements (free space required).
    streetAddress: URIRef  # The street address. For example, 1600 Amphitheatre Pkwy.
    subEvent: URIRef  # An Event that is part of this event. For example, a conference event includes many presentations, each of which is a subEvent of the conference.
    subEvents: URIRef  # Events that are a part of this event. For example, a conference event includes many presentations, each subEvents of the conference.
    subOrganization: URIRef  # A relationship between two organizations where the first includes the second, e.g., as a subsidiary. See also: the more specific 'department' property.
    subReservation: URIRef  # The individual reservations included in the package. Typically a repeated property.
    subjectOf: URIRef  # A CreativeWork or Event about this Thing.
    successorOf: URIRef  # A pointer from a newer variant of a product  to its previous, often discontinued predecessor.
    sugarContent: URIRef  # The number of grams of sugar.
    suggestedAnswer: URIRef  # An answer (possibly one of several, possibly incorrect) to a Question, e.g. on a Question/Answer site.
    suggestedGender: URIRef  # The gender of the person or audience.
    suggestedMaxAge: URIRef  # Maximal age recommended for viewing content.
    suggestedMinAge: URIRef  # Minimal age recommended for viewing content.
    suitableForDiet: URIRef  # Indicates a dietary restriction or guideline for which this recipe or menu item is suitable, e.g. diabetic, halal etc.
    superEvent: URIRef  # An event that this event is a part of. For example, a collection of individual music performances might each have a music festival as their superEvent.
    supply: URIRef  # A sub-property of instrument. A supply consumed when performing instructions or a direction.
    supportingData: URIRef  # Supporting data for a SoftwareApplication.
    surface: URIRef  # A material used as a surface in some artwork, e.g. Canvas, Paper, Wood, Board, etc.
    target: URIRef  # Indicates a target EntryPoint for an Action.
    targetCollection: URIRef  # A sub property of object. The collection target of the action.
    targetDescription: URIRef  # The description of a node in an established educational framework.
    targetName: URIRef  # The name of a node in an established educational framework.
    targetPlatform: URIRef  # Type of app development: phone, Metro style, desktop, XBox, etc.
    targetProduct: URIRef  # Target Operating System / Product to which the code applies.  If applies to several versions, just the product name can be used.
    targetUrl: URIRef  # The URL of a node in an established educational framework.
    taxID: URIRef  # The Tax / Fiscal ID of the organization or person, e.g. the TIN in the US or the CIF/NIF in Spain.
    telephone: URIRef  # The telephone number.
    temporal: URIRef  # The "temporal" property can be used in cases where more specific properties (e.g. <a class="localLink" href="http://schema.org/temporalCoverage">temporalCoverage</a>, <a class="localLink" href="http://schema.org/dateCreated">dateCreated</a>, <a class="localLink" href="http://schema.org/dateModified">dateModified</a>, <a class="localLink" href="http://schema.org/datePublished">datePublished</a>) are not known to be appropriate.
    temporalCoverage: URIRef  # The temporalCoverage of a CreativeWork indicates the period that the content applies to, i.e. that it describes, either as a DateTime or as a textual string indicating a time period in <a href="https://en.wikipedia.org/wiki/ISO_8601#Time_intervals">ISO 8601 time interval format</a>. In       the case of a Dataset it will typically indicate the relevant time period in a precise notation (e.g. for a 2011 census dataset, the year 2011 would be written "2011/2012"). Other forms of content e.g. ScholarlyArticle, Book, TVSeries or TVEpisode may indicate their temporalCoverage in broader terms - textually or via well-known URL.       Written works such as books may sometimes have precise temporal coverage too, e.g. a work set in 1939 - 1945 can be indicated in ISO 8601 interval format format via "1939/1945".<br/><br/>  Open-ended date ranges can be written with ".." in place of the end date. For example, "2015-11/.." indicates a range beginning in November 2015 and with no specified final date. This is tentative and might be updated in future when ISO 8601 is officially updated.
    text: URIRef  # The textual content of this CreativeWork.
    thumbnail: URIRef  # Thumbnail image for an image or video.
    thumbnailUrl: URIRef  # A thumbnail image relevant to the Thing.
    tickerSymbol: URIRef  # The exchange traded instrument associated with a Corporation object. The tickerSymbol is expressed as an exchange and an instrument name separated by a space character. For the exchange component of the tickerSymbol attribute, we recommend using the controlled vocabulary of Market Identifier Codes (MIC) specified in ISO15022.
    ticketNumber: URIRef  # The unique identifier for the ticket.
    ticketToken: URIRef  # Reference to an asset (e.g., Barcode, QR code image or PDF) usable for entrance.
    ticketedSeat: URIRef  # The seat associated with the ticket.
    timeRequired: URIRef  # Approximate or typical time it takes to work with or through this learning resource for the typical intended target audience, e.g. 'PT30M', 'PT1H25M'.
    title: URIRef  # The title of the job.
    toLocation: URIRef  # A sub property of location. The final location of the object or the agent after the action.
    toRecipient: URIRef  # A sub property of recipient. The recipient who was directly sent the message.
    tool: URIRef  # A sub property of instrument. An object used (but not consumed) when performing instructions or a direction.
    totalPaymentDue: URIRef  # The total amount due.
    totalPrice: URIRef  # The total price for the reservation or ticket, including applicable taxes, shipping, etc.<br/><br/>  Usage guidelines:<br/><br/>  <ul> <li>Use values from 0123456789 (Unicode 'DIGIT ZERO' (U+0030) to 'DIGIT NINE' (U+0039)) rather than superficially similiar Unicode symbols.</li> <li>Use '.' (Unicode 'FULL STOP' (U+002E)) rather than ',' to indicate a decimal point. Avoid using these symbols as a readability separator.</li> </ul>
    totalTime: URIRef  # The total time required to perform instructions or a direction (including time to prepare the supplies), in <a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601 duration format</a>.
    touristType: URIRef  # Attraction suitable for type(s) of tourist. eg. Children, visitors from a particular country, etc.
    track: URIRef  # A music recording (track)&#x2014;usually a single song. If an ItemList is given, the list should contain items of type MusicRecording.
    trackingNumber: URIRef  # Shipper tracking number.
    trackingUrl: URIRef  # Tracking url for the parcel delivery.
    tracks: URIRef  # A music recording (track)&#x2014;usually a single song.
    trailer: URIRef  # The trailer of a movie or tv/radio series, season, episode, etc.
    trainName: URIRef  # The name of the train (e.g. The Orient Express).
    trainNumber: URIRef  # The unique identifier for the train.
    transFatContent: URIRef  # The number of grams of trans fat.
    transcript: URIRef  # If this MediaObject is an AudioObject or VideoObject, the transcript of that object.
    translator: URIRef  # Organization or person who adapts a creative work to different languages, regional differences and technical requirements of a target market, or that translates during some event.
    typeOfBed: URIRef  # The type of bed to which the BedDetail refers, i.e. the type of bed available in the quantity indicated by quantity.
    typeOfGood: URIRef  # The product that this structured value is referring to.
    typicalAgeRange: URIRef  # The typical expected age range, e.g. '7-9', '11-'.
    underName: URIRef  # The person or organization the reservation or ticket is for.
    unitCode: URIRef  # The unit of measurement given using the UN/CEFACT Common Code (3 characters) or a URL. Other codes than the UN/CEFACT Common Code may be used with a prefix followed by a colon.
    unitText: URIRef  # A string or text indicating the unit of measurement. Useful if you cannot provide a standard unit code for <a href='unitCode'>unitCode</a>.
    unsaturatedFatContent: URIRef  # The number of grams of unsaturated fat.
    uploadDate: URIRef  # Date when this media object was uploaded to this site.
    upvoteCount: URIRef  # The number of upvotes this question, answer or comment has received from the community.
    url: URIRef  # URL of the item.
    urlTemplate: URIRef  # An url template (RFC6570) that will be used to construct the target of the execution of the action.
    userInteractionCount: URIRef  # The number of interactions for the CreativeWork using the WebSite or SoftwareApplication.
    validFor: URIRef  # The duration of validity of a permit or similar thing.
    validFrom: URIRef  # The date when the item becomes valid.
    validIn: URIRef  # The geographic area where a permit or similar thing is valid.
    validThrough: URIRef  # The date after when the item is not valid. For example the end of an offer, salary period, or a period of opening hours.
    validUntil: URIRef  # The date when the item is no longer valid.
    value: URIRef  # The value of the quantitative value or property value node.<br/><br/>  <ul> <li>For <a class="localLink" href="http://schema.org/QuantitativeValue">QuantitativeValue</a> and <a class="localLink" href="http://schema.org/MonetaryAmount">MonetaryAmount</a>, the recommended type for values is 'Number'.</li> <li>For <a class="localLink" href="http://schema.org/PropertyValue">PropertyValue</a>, it can be 'Text;', 'Number', 'Boolean', or 'StructuredValue'.</li> <li>Use values from 0123456789 (Unicode 'DIGIT ZERO' (U+0030) to 'DIGIT NINE' (U+0039)) rather than superficially similiar Unicode symbols.</li> <li>Use '.' (Unicode 'FULL STOP' (U+002E)) rather than ',' to indicate a decimal point. Avoid using these symbols as a readability separator.</li> </ul>
    valueAddedTaxIncluded: URIRef  # Specifies whether the applicable value-added tax (VAT) is included in the price specification or not.
    valueMaxLength: URIRef  # Specifies the allowed range for number of characters in a literal value.
    valueMinLength: URIRef  # Specifies the minimum allowed range for number of characters in a literal value.
    valueName: URIRef  # Indicates the name of the PropertyValueSpecification to be used in URL templates and form encoding in a manner analogous to HTML's input@name.
    valuePattern: URIRef  # Specifies a regular expression for testing literal values according to the HTML spec.
    valueReference: URIRef  # A pointer to a secondary value that provides additional information on the original value, e.g. a reference temperature.
    valueRequired: URIRef  # Whether the property must be filled in to complete the action.  Default is false.
    vatID: URIRef  # The Value-added Tax ID of the organization or person.
    vehicleConfiguration: URIRef  # A short text indicating the configuration of the vehicle, e.g. '5dr hatchback ST 2.5 MT 225 hp' or 'limited edition'.
    vehicleEngine: URIRef  # Information about the engine or engines of the vehicle.
    vehicleIdentificationNumber: URIRef  # The Vehicle Identification Number (VIN) is a unique serial number used by the automotive industry to identify individual motor vehicles.
    vehicleInteriorColor: URIRef  # The color or color combination of the interior of the vehicle.
    vehicleInteriorType: URIRef  # The type or material of the interior of the vehicle (e.g. synthetic fabric, leather, wood, etc.). While most interior types are characterized by the material used, an interior type can also be based on vehicle usage or target audience.
    vehicleModelDate: URIRef  # The release date of a vehicle model (often used to differentiate versions of the same make and model).
    vehicleSeatingCapacity: URIRef  # The number of passengers that can be seated in the vehicle, both in terms of the physical space available, and in terms of limitations set by law.<br/><br/>  Typical unit code(s): C62 for persons.
    vehicleTransmission: URIRef  # The type of component used for transmitting the power from a rotating power source to the wheels or other relevant component(s) ("gearbox" for cars).
    vendor: URIRef  # 'vendor' is an earlier term for 'seller'.
    version: URIRef  # The version of the CreativeWork embodied by a specified resource.
    video: URIRef  # An embedded video object.
    videoFormat: URIRef  # The type of screening or video broadcast used (e.g. IMAX, 3D, SD, HD, etc.).
    videoFrameSize: URIRef  # The frame size of the video.
    videoQuality: URIRef  # The quality of the video.
    volumeNumber: URIRef  # Identifies the volume of publication or multi-part work; for example, "iii" or "2".
    warranty: URIRef  # The warranty promise(s) included in the offer.
    warrantyPromise: URIRef  # The warranty promise(s) included in the offer.
    warrantyScope: URIRef  # The scope of the warranty promise.
    webCheckinTime: URIRef  # The time when a passenger can check into the flight online.
    weight: URIRef  # The weight of the product or person.
    width: URIRef  # The width of the item.
    winner: URIRef  # A sub property of participant. The winner of the action.
    wordCount: URIRef  # The number of words in the text of the Article.
    workExample: URIRef  # Example/instance/realization/derivation of the concept of this creative work. eg. The paperback edition, first edition, or eBook.
    workFeatured: URIRef  # A work featured in some event, e.g. exhibited in an ExhibitionEvent.        Specific subproperties are available for workPerformed (e.g. a play), or a workPresented (a Movie at a ScreeningEvent).
    workHours: URIRef  # The typical working hours for this job (e.g. 1st shift, night shift, 8am-5pm).
    workLocation: URIRef  # A contact location for a person's place of work.
    workPerformed: URIRef  # A work performed in some event, for example a play performed in a TheaterEvent.
    workPresented: URIRef  # The movie presented during this event.
    worksFor: URIRef  # Organizations that the person works for.
    worstRating: URIRef  # The lowest value allowed in this rating system. If worstRating is omitted, 1 is assumed.
    xpath: URIRef  # An XPath, e.g. of a <a class="localLink" href="http://schema.org/SpeakableSpecification">SpeakableSpecification</a> or <a class="localLink" href="http://schema.org/WebPageElement">WebPageElement</a>. In the latter case, multiple matches within a page can constitute a single conceptual "Web page element".
    yearlyRevenue: URIRef  # The size of the business in annual revenue.
    yearsInOperation: URIRef  # The age of the business.

    # http://www.w3.org/2000/01/rdf-schema#Class
    AMRadioChannel: URIRef  # A radio channel that uses AM.
    APIReference: URIRef  # Reference documentation for application programming interfaces (APIs).
    AboutPage: URIRef  # Web page type: About page.
    AcceptAction: URIRef  # The act of committing to/adopting an object.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/RejectAction">RejectAction</a>: The antonym of AcceptAction.</li> </ul>
    Accommodation: URIRef  # An accommodation is a place that can accommodate human beings, e.g. a hotel room, a camping pitch, or a meeting room. Many accommodations are for overnight stays, but this is not a mandatory requirement. For more specific types of accommodations not defined in schema.org, one can use additionalType with external vocabularies. <br /><br /> See also the <a href="/docs/hotels.html">dedicated document on the use of schema.org for marking up hotels and other forms of accommodations</a>.
    AccountingService: URIRef  # Accountancy business.<br/><br/>  As a <a class="localLink" href="http://schema.org/LocalBusiness">LocalBusiness</a> it can be described as a <a class="localLink" href="http://schema.org/provider">provider</a> of one or more <a class="localLink" href="http://schema.org/Service">Service</a>(s).
    AchieveAction: URIRef  # The act of accomplishing something via previous efforts. It is an instantaneous action rather than an ongoing process.
    Action: URIRef  # An action performed by a direct agent and indirect participants upon a direct object. Optionally happens at a location with the help of an inanimate instrument. The execution of the action may produce a result. Specific action sub-type documentation specifies the exact expectation of each argument/role.<br/><br/>  See also <a href="http://blog.schema.org/2014/04/announcing-schemaorg-actions.html">blog post</a> and <a href="http://schema.org/docs/actions.html">Actions overview document</a>.
    ActionAccessSpecification: URIRef  # A set of requirements that a must be fulfilled in order to perform an Action.
    ActionStatusType: URIRef  # The status of an Action.
    ActivateAction: URIRef  # The act of starting or activating a device or application (e.g. starting a timer or turning on a flashlight).
    AddAction: URIRef  # The act of editing by adding an object to a collection.
    AdministrativeArea: URIRef  # A geographical region, typically under the jurisdiction of a particular government.
    AdultEntertainment: URIRef  # An adult entertainment establishment.
    AggregateOffer: URIRef  # When a single product is associated with multiple offers (for example, the same pair of shoes is offered by different merchants), then AggregateOffer can be used.<br/><br/>  Note: AggregateOffers are normally expected to associate multiple offers that all share the same defined <a class="localLink" href="http://schema.org/businessFunction">businessFunction</a> value, or default to http://purl.org/goodrelations/v1#Sell if businessFunction is not explicitly defined.
    AggregateRating: URIRef  # The average rating based on multiple ratings or reviews.
    AgreeAction: URIRef  # The act of expressing a consistency of opinion with the object. An agent agrees to/about an object (a proposition, topic or theme) with participants.
    Airline: URIRef  # An organization that provides flights for passengers.
    Airport: URIRef  # An airport.
    AlignmentObject: URIRef  # An intangible item that describes an alignment between a learning resource and a node in an educational framework.<br/><br/>  Should not be used where the nature of the alignment can be described using a simple property, for example to express that a resource <a class="localLink" href="http://schema.org/teaches">teaches</a> or <a class="localLink" href="http://schema.org/assesses">assesses</a> a competency.
    AllocateAction: URIRef  # The act of organizing tasks/objects/events by associating resources to it.
    AmusementPark: URIRef  # An amusement park.
    AnimalShelter: URIRef  # Animal shelter.
    Answer: URIRef  # An answer offered to a question; perhaps correct, perhaps opinionated or wrong.
    Apartment: URIRef  # An apartment (in American English) or flat (in British English) is a self-contained housing unit (a type of residential real estate) that occupies only part of a building (Source: Wikipedia, the free encyclopedia, see <a href="http://en.wikipedia.org/wiki/Apartment">http://en.wikipedia.org/wiki/Apartment</a>).
    ApartmentComplex: URIRef  # Residence type: Apartment complex.
    AppendAction: URIRef  # The act of inserting at the end if an ordered collection.
    ApplyAction: URIRef  # The act of registering to an organization/service without the guarantee to receive it.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/RegisterAction">RegisterAction</a>: Unlike RegisterAction, ApplyAction has no guarantees that the application will be accepted.</li> </ul>
    Aquarium: URIRef  # Aquarium.
    ArriveAction: URIRef  # The act of arriving at a place. An agent arrives at a destination from a fromLocation, optionally with participants.
    ArtGallery: URIRef  # An art gallery.
    Article: URIRef  # An article, such as a news article or piece of investigative report. Newspapers and magazines have articles of many different types and this is intended to cover them all.<br/><br/>  See also <a href="http://blog.schema.org/2014/09/schemaorg-support-for-bibliographic_2.html">blog post</a>.
    AskAction: URIRef  # The act of posing a question / favor to someone.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/ReplyAction">ReplyAction</a>: Appears generally as a response to AskAction.</li> </ul>
    AssessAction: URIRef  # The act of forming one's opinion, reaction or sentiment.
    AssignAction: URIRef  # The act of allocating an action/event/task to some destination (someone or something).
    Attorney: URIRef  # Professional service: Attorney. <br/><br/>  This type is deprecated - <a class="localLink" href="http://schema.org/LegalService">LegalService</a> is more inclusive and less ambiguous.
    Audience: URIRef  # Intended audience for an item, i.e. the group for whom the item was created.
    AudioObject: URIRef  # An audio file.
    AuthorizeAction: URIRef  # The act of granting permission to an object.
    AutoBodyShop: URIRef  # Auto body shop.
    AutoDealer: URIRef  # An car dealership.
    AutoPartsStore: URIRef  # An auto parts store.
    AutoRental: URIRef  # A car rental business.
    AutoRepair: URIRef  # Car repair business.
    AutoWash: URIRef  # A car wash business.
    AutomatedTeller: URIRef  # ATM/cash machine.
    AutomotiveBusiness: URIRef  # Car repair, sales, or parts.
    Bakery: URIRef  # A bakery.
    BankAccount: URIRef  # A product or service offered by a bank whereby one may deposit, withdraw or transfer money and in some cases be paid interest.
    BankOrCreditUnion: URIRef  # Bank or credit union.
    BarOrPub: URIRef  # A bar or pub.
    Barcode: URIRef  # An image of a visual machine-readable code such as a barcode or QR code.
    Beach: URIRef  # Beach.
    BeautySalon: URIRef  # Beauty salon.
    BedAndBreakfast: URIRef  # Bed and breakfast. <br /><br /> See also the <a href="/docs/hotels.html">dedicated document on the use of schema.org for marking up hotels and other forms of accommodations</a>.
    BedDetails: URIRef  # An entity holding detailed information about the available bed types, e.g. the quantity of twin beds for a hotel room. For the single case of just one bed of a certain type, you can use bed directly with a text. See also <a class="localLink" href="http://schema.org/BedType">BedType</a> (under development).
    BedType: URIRef  # A type of bed. This is used for indicating the bed or beds available in an accommodation.
    BefriendAction: URIRef  # The act of forming a personal connection with someone (object) mutually/bidirectionally/symmetrically.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/FollowAction">FollowAction</a>: Unlike FollowAction, BefriendAction implies that the connection is reciprocal.</li> </ul>
    BikeStore: URIRef  # A bike store.
    Blog: URIRef  # A blog.
    BlogPosting: URIRef  # A blog post.
    BoardingPolicyType: URIRef  # A type of boarding policy used by an airline.
    BodyOfWater: URIRef  # A body of water, such as a sea, ocean, or lake.
    Book: URIRef  # A book.
    BookFormatType: URIRef  # The publication format of the book.
    BookSeries: URIRef  # A series of books. Included books can be indicated with the hasPart property.
    BookStore: URIRef  # A bookstore.
    BookmarkAction: URIRef  # An agent bookmarks/flags/labels/tags/marks an object.
    Boolean: URIRef  # Boolean: True or False.
    BorrowAction: URIRef  # The act of obtaining an object under an agreement to return it at a later date. Reciprocal of LendAction.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/LendAction">LendAction</a>: Reciprocal of BorrowAction.</li> </ul>
    BowlingAlley: URIRef  # A bowling alley.
    Brand: URIRef  # A brand is a name used by an organization or business person for labeling a product, product group, or similar.
    BreadcrumbList: URIRef  # A BreadcrumbList is an ItemList consisting of a chain of linked Web pages, typically described using at least their URL and their name, and typically ending with the current page.<br/><br/>  The <a class="localLink" href="http://schema.org/position">position</a> property is used to reconstruct the order of the items in a BreadcrumbList The convention is that a breadcrumb list has an <a class="localLink" href="http://schema.org/itemListOrder">itemListOrder</a> of <a class="localLink" href="http://schema.org/ItemListOrderAscending">ItemListOrderAscending</a> (lower values listed first), and that the first items in this list correspond to the "top" or beginning of the breadcrumb trail, e.g. with a site or section homepage. The specific values of 'position' are not assigned meaning for a BreadcrumbList, but they should be integers, e.g. beginning with '1' for the first item in the list.
    Brewery: URIRef  # Brewery.
    Bridge: URIRef  # A bridge.
    BroadcastChannel: URIRef  # A unique instance of a BroadcastService on a CableOrSatelliteService lineup.
    BroadcastEvent: URIRef  # An over the air or online broadcast event.
    BroadcastFrequencySpecification: URIRef  # The frequency in MHz and the modulation used for a particular BroadcastService.
    BroadcastService: URIRef  # A delivery service through which content is provided via broadcast over the air or online.
    BuddhistTemple: URIRef  # A Buddhist temple.
    BusReservation: URIRef  # A reservation for bus travel. <br/><br/>  Note: This type is for information about actual reservations, e.g. in confirmation emails or HTML pages with individual confirmations of reservations. For offers of tickets, use <a class="localLink" href="http://schema.org/Offer">Offer</a>.
    BusStation: URIRef  # A bus station.
    BusStop: URIRef  # A bus stop.
    BusTrip: URIRef  # A trip on a commercial bus line.
    BusinessAudience: URIRef  # A set of characteristics belonging to businesses, e.g. who compose an item's target audience.
    BusinessEntityType: URIRef  # A business entity type is a conceptual entity representing the legal form, the size, the main line of business, the position in the value chain, or any combination thereof, of an organization or business person.<br/><br/>  Commonly used values:<br/><br/>  <ul> <li>http://purl.org/goodrelations/v1#Business</li> <li>http://purl.org/goodrelations/v1#Enduser</li> <li>http://purl.org/goodrelations/v1#PublicInstitution</li> <li>http://purl.org/goodrelations/v1#Reseller</li> </ul>
    BusinessEvent: URIRef  # Event type: Business event.
    BusinessFunction: URIRef  # The business function specifies the type of activity or access (i.e., the bundle of rights) offered by the organization or business person through the offer. Typical are sell, rental or lease, maintenance or repair, manufacture / produce, recycle / dispose, engineering / construction, or installation. Proprietary specifications of access rights are also instances of this class.<br/><br/>  Commonly used values:<br/><br/>  <ul> <li>http://purl.org/goodrelations/v1#ConstructionInstallation</li> <li>http://purl.org/goodrelations/v1#Dispose</li> <li>http://purl.org/goodrelations/v1#LeaseOut</li> <li>http://purl.org/goodrelations/v1#Maintain</li> <li>http://purl.org/goodrelations/v1#ProvideService</li> <li>http://purl.org/goodrelations/v1#Repair</li> <li>http://purl.org/goodrelations/v1#Sell</li> <li>http://purl.org/goodrelations/v1#Buy</li> </ul>
    BuyAction: URIRef  # The act of giving money to a seller in exchange for goods or services rendered. An agent buys an object, product, or service from a seller for a price. Reciprocal of SellAction.
    CableOrSatelliteService: URIRef  # A service which provides access to media programming like TV or radio. Access may be via cable or satellite.
    CafeOrCoffeeShop: URIRef  # A cafe or coffee shop.
    Campground: URIRef  # A camping site, campsite, or <a class="localLink" href="http://schema.org/Campground">Campground</a> is a place used for overnight stay in the outdoors, typically containing individual <a class="localLink" href="http://schema.org/CampingPitch">CampingPitch</a> locations. <br/><br/>  In British English a campsite is an area, usually divided into a number of pitches, where people can camp overnight using tents or camper vans or caravans; this British English use of the word is synonymous with the American English expression campground. In American English the term campsite generally means an area where an individual, family, group, or military unit can pitch a tent or park a camper; a campground may contain many campsites (Source: Wikipedia see <a href="https://en.wikipedia.org/wiki/Campsite">https://en.wikipedia.org/wiki/Campsite</a>).<br/><br/>  See also the dedicated <a href="/docs/hotels.html">document on the use of schema.org for marking up hotels and other forms of accommodations</a>.
    CampingPitch: URIRef  # A <a class="localLink" href="http://schema.org/CampingPitch">CampingPitch</a> is an individual place for overnight stay in the outdoors, typically being part of a larger camping site, or <a class="localLink" href="http://schema.org/Campground">Campground</a>.<br/><br/>  In British English a campsite, or campground, is an area, usually divided into a number of pitches, where people can camp overnight using tents or camper vans or caravans; this British English use of the word is synonymous with the American English expression campground. In American English the term campsite generally means an area where an individual, family, group, or military unit can pitch a tent or park a camper; a campground may contain many campsites. (Source: Wikipedia see <a href="https://en.wikipedia.org/wiki/Campsite">https://en.wikipedia.org/wiki/Campsite</a>).<br/><br/>  See also the dedicated <a href="/docs/hotels.html">document on the use of schema.org for marking up hotels and other forms of accommodations</a>.
    Canal: URIRef  # A canal, like the Panama Canal.
    CancelAction: URIRef  # The act of asserting that a future event/action is no longer going to happen.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/ConfirmAction">ConfirmAction</a>: The antonym of CancelAction.</li> </ul>
    Car: URIRef  # A car is a wheeled, self-powered motor vehicle used for transportation.
    Casino: URIRef  # A casino.
    CatholicChurch: URIRef  # A Catholic church.
    Cemetery: URIRef  # A graveyard.
    CheckAction: URIRef  # An agent inspects, determines, investigates, inquires, or examines an object's accuracy, quality, condition, or state.
    CheckInAction: URIRef  # The act of an agent communicating (service provider, social media, etc) their arrival by registering/confirming for a previously reserved service (e.g. flight check in) or at a place (e.g. hotel), possibly resulting in a result (boarding pass, etc).<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/CheckOutAction">CheckOutAction</a>: The antonym of CheckInAction.</li> <li><a class="localLink" href="http://schema.org/ArriveAction">ArriveAction</a>: Unlike ArriveAction, CheckInAction implies that the agent is informing/confirming the start of a previously reserved service.</li> <li><a class="localLink" href="http://schema.org/ConfirmAction">ConfirmAction</a>: Unlike ConfirmAction, CheckInAction implies that the agent is informing/confirming the <em>start</em> of a previously reserved service rather than its validity/existence.</li> </ul>
    CheckOutAction: URIRef  # The act of an agent communicating (service provider, social media, etc) their departure of a previously reserved service (e.g. flight check in) or place (e.g. hotel).<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/CheckInAction">CheckInAction</a>: The antonym of CheckOutAction.</li> <li><a class="localLink" href="http://schema.org/DepartAction">DepartAction</a>: Unlike DepartAction, CheckOutAction implies that the agent is informing/confirming the end of a previously reserved service.</li> <li><a class="localLink" href="http://schema.org/CancelAction">CancelAction</a>: Unlike CancelAction, CheckOutAction implies that the agent is informing/confirming the end of a previously reserved service.</li> </ul>
    CheckoutPage: URIRef  # Web page type: Checkout page.
    ChildCare: URIRef  # A Childcare center.
    ChildrensEvent: URIRef  # Event type: Children's event.
    ChooseAction: URIRef  # The act of expressing a preference from a set of options or a large or unbounded set of choices/options.
    Church: URIRef  # A church.
    City: URIRef  # A city or town.
    CityHall: URIRef  # A city hall.
    CivicStructure: URIRef  # A public structure, such as a town hall or concert hall.
    ClaimReview: URIRef  # A fact-checking review of claims made (or reported) in some creative work (referenced via itemReviewed).
    Clip: URIRef  # A short TV or radio program or a segment/part of a program.
    ClothingStore: URIRef  # A clothing store.
    Code: URIRef  # Computer programming source code. Example: Full (compile ready) solutions, code snippet samples, scripts, templates.
    CollectionPage: URIRef  # Web page type: Collection page.
    CollegeOrUniversity: URIRef  # A college, university, or other third-level educational institution.
    ComedyClub: URIRef  # A comedy club.
    ComedyEvent: URIRef  # Event type: Comedy event.
    Comment: URIRef  # A comment on an item - for example, a comment on a blog post. The comment's content is expressed via the <a class="localLink" href="http://schema.org/text">text</a> property, and its topic via <a class="localLink" href="http://schema.org/about">about</a>, properties shared with all CreativeWorks.
    CommentAction: URIRef  # The act of generating a comment about a subject.
    CommunicateAction: URIRef  # The act of conveying information to another person via a communication medium (instrument) such as speech, email, or telephone conversation.
    CompoundPriceSpecification: URIRef  # A compound price specification is one that bundles multiple prices that all apply in combination for different dimensions of consumption. Use the name property of the attached unit price specification for indicating the dimension of a price component (e.g. "electricity" or "final cleaning").
    ComputerLanguage: URIRef  # This type covers computer programming languages such as Scheme and Lisp, as well as other language-like computer representations. Natural languages are best represented with the <a class="localLink" href="http://schema.org/Language">Language</a> type.
    ComputerStore: URIRef  # A computer store.
    ConfirmAction: URIRef  # The act of notifying someone that a future event/action is going to happen as expected.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/CancelAction">CancelAction</a>: The antonym of ConfirmAction.</li> </ul>
    ConsumeAction: URIRef  # The act of ingesting information/resources/food.
    ContactPage: URIRef  # Web page type: Contact page.
    ContactPoint: URIRef  # A contact point&#x2014;for example, a Customer Complaints department.
    ContactPointOption: URIRef  # Enumerated options related to a ContactPoint.
    Continent: URIRef  # One of the continents (for example, Europe or Africa).
    ControlAction: URIRef  # An agent controls a device or application.
    ConvenienceStore: URIRef  # A convenience store.
    Conversation: URIRef  # One or more messages between organizations or people on a particular topic. Individual messages can be linked to the conversation with isPartOf or hasPart properties.
    CookAction: URIRef  # The act of producing/preparing food.
    Corporation: URIRef  # Organization: A business corporation.
    Country: URIRef  # A country.
    Course: URIRef  # A description of an educational course which may be offered as distinct instances at which take place at different times or take place at different locations, or be offered through different media or modes of study. An educational course is a sequence of one or more educational events and/or creative works which aims to build knowledge, competence or ability of learners.
    CourseInstance: URIRef  # An instance of a <a class="localLink" href="http://schema.org/Course">Course</a> which is distinct from other instances because it is offered at a different time or location or through different media or modes of study or to a specific section of students.
    Courthouse: URIRef  # A courthouse.
    CreateAction: URIRef  # The act of deliberately creating/producing/generating/building a result out of the agent.
    CreativeWork: URIRef  # The most generic kind of creative work, including books, movies, photographs, software programs, etc.
    CreativeWorkSeason: URIRef  # A media season e.g. tv, radio, video game etc.
    CreativeWorkSeries: URIRef  # A CreativeWorkSeries in schema.org is a group of related items, typically but not necessarily of the same kind. CreativeWorkSeries are usually organized into some order, often chronological. Unlike <a class="localLink" href="http://schema.org/ItemList">ItemList</a> which is a general purpose data structure for lists of things, the emphasis with CreativeWorkSeries is on published materials (written e.g. books and periodicals, or media such as tv, radio and games).<br/><br/>  Specific subtypes are available for describing <a class="localLink" href="http://schema.org/TVSeries">TVSeries</a>, <a class="localLink" href="http://schema.org/RadioSeries">RadioSeries</a>, <a class="localLink" href="http://schema.org/MovieSeries">MovieSeries</a>, <a class="localLink" href="http://schema.org/BookSeries">BookSeries</a>, <a class="localLink" href="http://schema.org/Periodical">Periodical</a> and <a class="localLink" href="http://schema.org/VideoGameSeries">VideoGameSeries</a>. In each case, the <a class="localLink" href="http://schema.org/hasPart">hasPart</a> / <a class="localLink" href="http://schema.org/isPartOf">isPartOf</a> properties can be used to relate the CreativeWorkSeries to its parts. The general CreativeWorkSeries type serves largely just to organize these more specific and practical subtypes.<br/><br/>  It is common for properties applicable to an item from the series to be usefully applied to the containing group. Schema.org attempts to anticipate some of these cases, but publishers should be free to apply properties of the series parts to the series as a whole wherever they seem appropriate.
    CreditCard: URIRef  # A card payment method of a particular brand or name.  Used to mark up a particular payment method and/or the financial product/service that supplies the card account.<br/><br/>  Commonly used values:<br/><br/>  <ul> <li>http://purl.org/goodrelations/v1#AmericanExpress</li> <li>http://purl.org/goodrelations/v1#DinersClub</li> <li>http://purl.org/goodrelations/v1#Discover</li> <li>http://purl.org/goodrelations/v1#JCB</li> <li>http://purl.org/goodrelations/v1#MasterCard</li> <li>http://purl.org/goodrelations/v1#VISA</li> </ul>
    Crematorium: URIRef  # A crematorium.
    CurrencyConversionService: URIRef  # A service to convert funds from one currency to another currency.
    DanceEvent: URIRef  # Event type: A social dance.
    DanceGroup: URIRef  # A dance group&#x2014;for example, the Alvin Ailey Dance Theater or Riverdance.
    DataCatalog: URIRef  # A collection of datasets.
    DataDownload: URIRef  # A dataset in downloadable form.
    DataFeed: URIRef  # A single feed providing structured information about one or more entities or topics.
    DataFeedItem: URIRef  # A single item within a larger data feed.
    DataType: URIRef  # The basic data types such as Integers, Strings, etc.
    Dataset: URIRef  # A body of structured information describing some topic(s) of interest.
    Date: URIRef  # A date value in <a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601 date format</a>.
    DateTime: URIRef  # A combination of date and time of day in the form [-]CCYY-MM-DDThh:mm:ss[Z|(+|-)hh:mm] (see Chapter 5.4 of ISO 8601).
    DatedMoneySpecification: URIRef  # A DatedMoneySpecification represents monetary values with optional start and end dates. For example, this could represent an employee's salary over a specific period of time. <strong>Note:</strong> This type has been superseded by <a class="localLink" href="http://schema.org/MonetaryAmount">MonetaryAmount</a> use of that type is recommended
    DayOfWeek: URIRef  # The day of the week, e.g. used to specify to which day the opening hours of an OpeningHoursSpecification refer.<br/><br/>  Originally, URLs from <a href="http://purl.org/goodrelations/v1">GoodRelations</a> were used (for <a class="localLink" href="http://schema.org/Monday">Monday</a>, <a class="localLink" href="http://schema.org/Tuesday">Tuesday</a>, <a class="localLink" href="http://schema.org/Wednesday">Wednesday</a>, <a class="localLink" href="http://schema.org/Thursday">Thursday</a>, <a class="localLink" href="http://schema.org/Friday">Friday</a>, <a class="localLink" href="http://schema.org/Saturday">Saturday</a>, <a class="localLink" href="http://schema.org/Sunday">Sunday</a> plus a special entry for <a class="localLink" href="http://schema.org/PublicHolidays">PublicHolidays</a>); these have now been integrated directly into schema.org.
    DaySpa: URIRef  # A day spa.
    DeactivateAction: URIRef  # The act of stopping or deactivating a device or application (e.g. stopping a timer or turning off a flashlight).
    DefenceEstablishment: URIRef  # A defence establishment, such as an army or navy base.
    DeleteAction: URIRef  # The act of editing a recipient by removing one of its objects.
    DeliveryChargeSpecification: URIRef  # The price for the delivery of an offer using a particular delivery method.
    DeliveryEvent: URIRef  # An event involving the delivery of an item.
    DeliveryMethod: URIRef  # A delivery method is a standardized procedure for transferring the product or service to the destination of fulfillment chosen by the customer. Delivery methods are characterized by the means of transportation used, and by the organization or group that is the contracting party for the sending organization or person.<br/><br/>  Commonly used values:<br/><br/>  <ul> <li>http://purl.org/goodrelations/v1#DeliveryModeDirectDownload</li> <li>http://purl.org/goodrelations/v1#DeliveryModeFreight</li> <li>http://purl.org/goodrelations/v1#DeliveryModeMail</li> <li>http://purl.org/goodrelations/v1#DeliveryModeOwnFleet</li> <li>http://purl.org/goodrelations/v1#DeliveryModePickUp</li> <li>http://purl.org/goodrelations/v1#DHL</li> <li>http://purl.org/goodrelations/v1#FederalExpress</li> <li>http://purl.org/goodrelations/v1#UPS</li> </ul>
    Demand: URIRef  # A demand entity represents the public, not necessarily binding, not necessarily exclusive, announcement by an organization or person to seek a certain type of goods or services. For describing demand using this type, the very same properties used for Offer apply.
    Dentist: URIRef  # A dentist.
    DepartAction: URIRef  # The act of  departing from a place. An agent departs from an fromLocation for a destination, optionally with participants.
    DepartmentStore: URIRef  # A department store.
    DepositAccount: URIRef  # A type of Bank Account with a main purpose of depositing funds to gain interest or other benefits.
    DigitalDocument: URIRef  # An electronic file or document.
    DigitalDocumentPermission: URIRef  # A permission for a particular person or group to access a particular file.
    DigitalDocumentPermissionType: URIRef  # A type of permission which can be granted for accessing a digital document.
    DisagreeAction: URIRef  # The act of expressing a difference of opinion with the object. An agent disagrees to/about an object (a proposition, topic or theme) with participants.
    DiscoverAction: URIRef  # The act of discovering/finding an object.
    DiscussionForumPosting: URIRef  # A posting to a discussion forum.
    DislikeAction: URIRef  # The act of expressing a negative sentiment about the object. An agent dislikes an object (a proposition, topic or theme) with participants.
    Distance: URIRef  # Properties that take Distances as values are of the form '&lt;Number&gt; &lt;Length unit of measure&gt;'. E.g., '7 ft'.
    Distillery: URIRef  # A distillery.
    DonateAction: URIRef  # The act of providing goods, services, or money without compensation, often for philanthropic reasons.
    DownloadAction: URIRef  # The act of downloading an object.
    DrawAction: URIRef  # The act of producing a visual/graphical representation of an object, typically with a pen/pencil and paper as instruments.
    DrinkAction: URIRef  # The act of swallowing liquids.
    DriveWheelConfigurationValue: URIRef  # A value indicating which roadwheels will receive torque.
    DryCleaningOrLaundry: URIRef  # A dry-cleaning business.
    Duration: URIRef  # Quantity: Duration (use <a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601 duration format</a>).
    EatAction: URIRef  # The act of swallowing solid objects.
    EducationEvent: URIRef  # Event type: Education event.
    EducationalAudience: URIRef  # An EducationalAudience.
    EducationalOrganization: URIRef  # An educational organization.
    Electrician: URIRef  # An electrician.
    ElectronicsStore: URIRef  # An electronics store.
    ElementarySchool: URIRef  # An elementary school.
    EmailMessage: URIRef  # An email message.
    Embassy: URIRef  # An embassy.
    EmergencyService: URIRef  # An emergency service, such as a fire station or ER.
    EmployeeRole: URIRef  # A subclass of OrganizationRole used to describe employee relationships.
    EmployerAggregateRating: URIRef  # An aggregate rating of an Organization related to its role as an employer.
    EmploymentAgency: URIRef  # An employment agency.
    EndorseAction: URIRef  # An agent approves/certifies/likes/supports/sanction an object.
    EndorsementRating: URIRef  # An EndorsementRating is a rating that expresses some level of endorsement, for example inclusion in a "critic's pick" blog, a "Like" or "+1" on a social network. It can be considered the <a class="localLink" href="http://schema.org/result">result</a> of an <a class="localLink" href="http://schema.org/EndorseAction">EndorseAction</a> in which the <a class="localLink" href="http://schema.org/object">object</a> of the action is rated positively by some <a class="localLink" href="http://schema.org/agent">agent</a>. As is common elsewhere in schema.org, it is sometimes more useful to describe the results of such an action without explicitly describing the <a class="localLink" href="http://schema.org/Action">Action</a>.<br/><br/>  An <a class="localLink" href="http://schema.org/EndorsementRating">EndorsementRating</a> may be part of a numeric scale or organized system, but this is not required: having an explicit type for indicating a positive, endorsement rating is particularly useful in the absence of numeric scales as it helps consumers understand that the rating is broadly positive.
    Energy: URIRef  # Properties that take Energy as values are of the form '&lt;Number&gt; &lt;Energy unit of measure&gt;'.
    EngineSpecification: URIRef  # Information about the engine of the vehicle. A vehicle can have multiple engines represented by multiple engine specification entities.
    EntertainmentBusiness: URIRef  # A business providing entertainment.
    EntryPoint: URIRef  # An entry point, within some Web-based protocol.
    Enumeration: URIRef  # Lists or enumerations—for example, a list of cuisines or music genres, etc.
    Episode: URIRef  # A media episode (e.g. TV, radio, video game) which can be part of a series or season.
    Event: URIRef  # An event happening at a certain time and location, such as a concert, lecture, or festival. Ticketing information may be added via the <a class="localLink" href="http://schema.org/offers">offers</a> property. Repeated events may be structured as separate Event objects.
    EventReservation: URIRef  # A reservation for an event like a concert, sporting event, or lecture.<br/><br/>  Note: This type is for information about actual reservations, e.g. in confirmation emails or HTML pages with individual confirmations of reservations. For offers of tickets, use <a class="localLink" href="http://schema.org/Offer">Offer</a>.
    EventStatusType: URIRef  # EventStatusType is an enumeration type whose instances represent several states that an Event may be in.
    EventVenue: URIRef  # An event venue.
    ExerciseAction: URIRef  # The act of participating in exertive activity for the purposes of improving health and fitness.
    ExerciseGym: URIRef  # A gym.
    ExhibitionEvent: URIRef  # Event type: Exhibition event, e.g. at a museum, library, archive, tradeshow, ...
    FAQPage: URIRef  # A <a class="localLink" href="http://schema.org/FAQPage">FAQPage</a> is a <a class="localLink" href="http://schema.org/WebPage">WebPage</a> presenting one or more "<a href="https://en.wikipedia.org/wiki/FAQ">Frequently asked questions</a>" (see also <a class="localLink" href="http://schema.org/QAPage">QAPage</a>).
    FMRadioChannel: URIRef  # A radio channel that uses FM.
    FastFoodRestaurant: URIRef  # A fast-food restaurant.
    Festival: URIRef  # Event type: Festival.
    FilmAction: URIRef  # The act of capturing sound and moving images on film, video, or digitally.
    FinancialProduct: URIRef  # A product provided to consumers and businesses by financial institutions such as banks, insurance companies, brokerage firms, consumer finance companies, and investment companies which comprise the financial services industry.
    FinancialService: URIRef  # Financial services business.
    FindAction: URIRef  # The act of finding an object.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/SearchAction">SearchAction</a>: FindAction is generally lead by a SearchAction, but not necessarily.</li> </ul>
    FireStation: URIRef  # A fire station. With firemen.
    Flight: URIRef  # An airline flight.
    FlightReservation: URIRef  # A reservation for air travel.<br/><br/>  Note: This type is for information about actual reservations, e.g. in confirmation emails or HTML pages with individual confirmations of reservations. For offers of tickets, use <a class="localLink" href="http://schema.org/Offer">Offer</a>.
    Float: URIRef  # Data type: Floating number.
    Florist: URIRef  # A florist.
    FollowAction: URIRef  # The act of forming a personal connection with someone/something (object) unidirectionally/asymmetrically to get updates polled from.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/BefriendAction">BefriendAction</a>: Unlike BefriendAction, FollowAction implies that the connection is <em>not</em> necessarily reciprocal.</li> <li><a class="localLink" href="http://schema.org/SubscribeAction">SubscribeAction</a>: Unlike SubscribeAction, FollowAction implies that the follower acts as an active agent constantly/actively polling for updates.</li> <li><a class="localLink" href="http://schema.org/RegisterAction">RegisterAction</a>: Unlike RegisterAction, FollowAction implies that the agent is interested in continuing receiving updates from the object.</li> <li><a class="localLink" href="http://schema.org/JoinAction">JoinAction</a>: Unlike JoinAction, FollowAction implies that the agent is interested in getting updates from the object.</li> <li><a class="localLink" href="http://schema.org/TrackAction">TrackAction</a>: Unlike TrackAction, FollowAction refers to the polling of updates of all aspects of animate objects rather than the location of inanimate objects (e.g. you track a package, but you don't follow it).</li> </ul>
    FoodEstablishment: URIRef  # A food-related business.
    FoodEstablishmentReservation: URIRef  # A reservation to dine at a food-related business.<br/><br/>  Note: This type is for information about actual reservations, e.g. in confirmation emails or HTML pages with individual confirmations of reservations.
    FoodEvent: URIRef  # Event type: Food event.
    FoodService: URIRef  # A food service, like breakfast, lunch, or dinner.
    FurnitureStore: URIRef  # A furniture store.
    Game: URIRef  # The Game type represents things which are games. These are typically rule-governed recreational activities, e.g. role-playing games in which players assume the role of characters in a fictional setting.
    GamePlayMode: URIRef  # Indicates whether this game is multi-player, co-op or single-player.
    GameServer: URIRef  # Server that provides game interaction in a multiplayer game.
    GameServerStatus: URIRef  # Status of a game server.
    GardenStore: URIRef  # A garden store.
    GasStation: URIRef  # A gas station.
    GatedResidenceCommunity: URIRef  # Residence type: Gated community.
    GenderType: URIRef  # An enumeration of genders.
    GeneralContractor: URIRef  # A general contractor.
    GeoCircle: URIRef  # A GeoCircle is a GeoShape representing a circular geographic area. As it is a GeoShape           it provides the simple textual property 'circle', but also allows the combination of postalCode alongside geoRadius.           The center of the circle can be indicated via the 'geoMidpoint' property, or more approximately using 'address', 'postalCode'.
    GeoCoordinates: URIRef  # The geographic coordinates of a place or event.
    GeoShape: URIRef  # The geographic shape of a place. A GeoShape can be described using several properties whose values are based on latitude/longitude pairs. Either whitespace or commas can be used to separate latitude and longitude; whitespace should be used when writing a list of several such points.
    GiveAction: URIRef  # The act of transferring ownership of an object to a destination. Reciprocal of TakeAction.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/TakeAction">TakeAction</a>: Reciprocal of GiveAction.</li> <li><a class="localLink" href="http://schema.org/SendAction">SendAction</a>: Unlike SendAction, GiveAction implies that ownership is being transferred (e.g. I may send my laptop to you, but that doesn't mean I'm giving it to you).</li> </ul>
    GolfCourse: URIRef  # A golf course.
    GovernmentBuilding: URIRef  # A government building.
    GovernmentOffice: URIRef  # A government office&#x2014;for example, an IRS or DMV office.
    GovernmentOrganization: URIRef  # A governmental organization or agency.
    GovernmentPermit: URIRef  # A permit issued by a government agency.
    GovernmentService: URIRef  # A service provided by a government organization, e.g. food stamps, veterans benefits, etc.
    GroceryStore: URIRef  # A grocery store.
    HVACBusiness: URIRef  # A business that provide Heating, Ventilation and Air Conditioning services.
    HairSalon: URIRef  # A hair salon.
    HardwareStore: URIRef  # A hardware store.
    HealthAndBeautyBusiness: URIRef  # Health and beauty.
    HealthClub: URIRef  # A health club.
    HighSchool: URIRef  # A high school.
    HinduTemple: URIRef  # A Hindu temple.
    HobbyShop: URIRef  # A store that sells materials useful or necessary for various hobbies.
    HomeAndConstructionBusiness: URIRef  # A construction business.<br/><br/>  A HomeAndConstructionBusiness is a <a class="localLink" href="http://schema.org/LocalBusiness">LocalBusiness</a> that provides services around homes and buildings.<br/><br/>  As a <a class="localLink" href="http://schema.org/LocalBusiness">LocalBusiness</a> it can be described as a <a class="localLink" href="http://schema.org/provider">provider</a> of one or more <a class="localLink" href="http://schema.org/Service">Service</a>(s).
    HomeGoodsStore: URIRef  # A home goods store.
    Hospital: URIRef  # A hospital.
    Hostel: URIRef  # A hostel - cheap accommodation, often in shared dormitories. <br /><br /> See also the <a href="/docs/hotels.html">dedicated document on the use of schema.org for marking up hotels and other forms of accommodations</a>.
    Hotel: URIRef  # A hotel is an establishment that provides lodging paid on a short-term basis (Source: Wikipedia, the free encyclopedia, see http://en.wikipedia.org/wiki/Hotel). <br /><br /> See also the <a href="/docs/hotels.html">dedicated document on the use of schema.org for marking up hotels and other forms of accommodations</a>.
    HotelRoom: URIRef  # A hotel room is a single room in a hotel. <br /><br /> See also the <a href="/docs/hotels.html">dedicated document on the use of schema.org for marking up hotels and other forms of accommodations</a>.
    House: URIRef  # A house is a building or structure that has the ability to be occupied for habitation by humans or other creatures (Source: Wikipedia, the free encyclopedia, see <a href="http://en.wikipedia.org/wiki/House">http://en.wikipedia.org/wiki/House</a>).
    HousePainter: URIRef  # A house painting service.
    HowTo: URIRef  # Instructions that explain how to achieve a result by performing a sequence of steps.
    HowToDirection: URIRef  # A direction indicating a single action to do in the instructions for how to achieve a result.
    HowToItem: URIRef  # An item used as either a tool or supply when performing the instructions for how to to achieve a result.
    HowToSection: URIRef  # A sub-grouping of steps in the instructions for how to achieve a result (e.g. steps for making a pie crust within a pie recipe).
    HowToStep: URIRef  # A step in the instructions for how to achieve a result. It is an ordered list with HowToDirection and/or HowToTip items.
    HowToSupply: URIRef  # A supply consumed when performing the instructions for how to achieve a result.
    HowToTip: URIRef  # An explanation in the instructions for how to achieve a result. It provides supplementary information about a technique, supply, author's preference, etc. It can explain what could be done, or what should not be done, but doesn't specify what should be done (see HowToDirection).
    HowToTool: URIRef  # A tool used (but not consumed) when performing instructions for how to achieve a result.
    IceCreamShop: URIRef  # An ice cream shop.
    IgnoreAction: URIRef  # The act of intentionally disregarding the object. An agent ignores an object.
    ImageGallery: URIRef  # Web page type: Image gallery page.
    ImageObject: URIRef  # An image file.
    IndividualProduct: URIRef  # A single, identifiable product instance (e.g. a laptop with a particular serial number).
    InformAction: URIRef  # The act of notifying someone of information pertinent to them, with no expectation of a response.
    InsertAction: URIRef  # The act of adding at a specific location in an ordered collection.
    InstallAction: URIRef  # The act of installing an application.
    InsuranceAgency: URIRef  # An Insurance agency.
    Intangible: URIRef  # A utility class that serves as the umbrella for a number of 'intangible' things such as quantities, structured values, etc.
    Integer: URIRef  # Data type: Integer.
    InteractAction: URIRef  # The act of interacting with another person or organization.
    InteractionCounter: URIRef  # A summary of how users have interacted with this CreativeWork. In most cases, authors will use a subtype to specify the specific type of interaction.
    InternetCafe: URIRef  # An internet cafe.
    InvestmentOrDeposit: URIRef  # A type of financial product that typically requires the client to transfer funds to a financial service in return for potential beneficial financial return.
    InviteAction: URIRef  # The act of asking someone to attend an event. Reciprocal of RsvpAction.
    Invoice: URIRef  # A statement of the money due for goods or services; a bill.
    ItemAvailability: URIRef  # A list of possible product availability options.
    ItemList: URIRef  # A list of items of any sort&#x2014;for example, Top 10 Movies About Weathermen, or Top 100 Party Songs. Not to be confused with HTML lists, which are often used only for formatting.
    ItemListOrderType: URIRef  # Enumerated for values for itemListOrder for indicating how an ordered ItemList is organized.
    ItemPage: URIRef  # A page devoted to a single item, such as a particular product or hotel.
    JewelryStore: URIRef  # A jewelry store.
    JobPosting: URIRef  # A listing that describes a job opening in a certain organization.
    JoinAction: URIRef  # An agent joins an event/group with participants/friends at a location.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/RegisterAction">RegisterAction</a>: Unlike RegisterAction, JoinAction refers to joining a group/team of people.</li> <li><a class="localLink" href="http://schema.org/SubscribeAction">SubscribeAction</a>: Unlike SubscribeAction, JoinAction does not imply that you'll be receiving updates.</li> <li><a class="localLink" href="http://schema.org/FollowAction">FollowAction</a>: Unlike FollowAction, JoinAction does not imply that you'll be polling for updates.</li> </ul>
    LakeBodyOfWater: URIRef  # A lake (for example, Lake Pontrachain).
    Landform: URIRef  # A landform or physical feature.  Landform elements include mountains, plains, lakes, rivers, seascape and oceanic waterbody interface features such as bays, peninsulas, seas and so forth, including sub-aqueous terrain features such as submersed mountain ranges, volcanoes, and the great ocean basins.
    LandmarksOrHistoricalBuildings: URIRef  # An historical landmark or building.
    Language: URIRef  # Natural languages such as Spanish, Tamil, Hindi, English, etc. Formal language code tags expressed in <a href="https://en.wikipedia.org/wiki/IETF_language_tag">BCP 47</a> can be used via the <a class="localLink" href="http://schema.org/alternateName">alternateName</a> property. The Language type previously also covered programming languages such as Scheme and Lisp, which are now best represented using <a class="localLink" href="http://schema.org/ComputerLanguage">ComputerLanguage</a>.
    LeaveAction: URIRef  # An agent leaves an event / group with participants/friends at a location.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/JoinAction">JoinAction</a>: The antonym of LeaveAction.</li> <li><a class="localLink" href="http://schema.org/UnRegisterAction">UnRegisterAction</a>: Unlike UnRegisterAction, LeaveAction implies leaving a group/team of people rather than a service.</li> </ul>
    LegalService: URIRef  # A LegalService is a business that provides legally-oriented services, advice and representation, e.g. law firms.<br/><br/>  As a <a class="localLink" href="http://schema.org/LocalBusiness">LocalBusiness</a> it can be described as a <a class="localLink" href="http://schema.org/provider">provider</a> of one or more <a class="localLink" href="http://schema.org/Service">Service</a>(s).
    LegislativeBuilding: URIRef  # A legislative building&#x2014;for example, the state capitol.
    LendAction: URIRef  # The act of providing an object under an agreement that it will be returned at a later date. Reciprocal of BorrowAction.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/BorrowAction">BorrowAction</a>: Reciprocal of LendAction.</li> </ul>
    Library: URIRef  # A library.
    LikeAction: URIRef  # The act of expressing a positive sentiment about the object. An agent likes an object (a proposition, topic or theme) with participants.
    LiquorStore: URIRef  # A shop that sells alcoholic drinks such as wine, beer, whisky and other spirits.
    ListItem: URIRef  # An list item, e.g. a step in a checklist or how-to description.
    ListenAction: URIRef  # The act of consuming audio content.
    LiteraryEvent: URIRef  # Event type: Literary event.
    LiveBlogPosting: URIRef  # A blog post intended to provide a rolling textual coverage of an ongoing event through continuous updates.
    LoanOrCredit: URIRef  # A financial product for the loaning of an amount of money under agreed terms and charges.
    LocalBusiness: URIRef  # A particular physical business or branch of an organization. Examples of LocalBusiness include a restaurant, a particular branch of a restaurant chain, a branch of a bank, a medical practice, a club, a bowling alley, etc.
    LocationFeatureSpecification: URIRef  # Specifies a location feature by providing a structured value representing a feature of an accommodation as a property-value pair of varying degrees of formality.
    LockerDelivery: URIRef  # A DeliveryMethod in which an item is made available via locker.
    Locksmith: URIRef  # A locksmith.
    LodgingBusiness: URIRef  # A lodging business, such as a motel, hotel, or inn.
    LodgingReservation: URIRef  # A reservation for lodging at a hotel, motel, inn, etc.<br/><br/>  Note: This type is for information about actual reservations, e.g. in confirmation emails or HTML pages with individual confirmations of reservations.
    LoseAction: URIRef  # The act of being defeated in a competitive activity.
    Map: URIRef  # A map.
    MapCategoryType: URIRef  # An enumeration of several kinds of Map.
    MarryAction: URIRef  # The act of marrying a person.
    Mass: URIRef  # Properties that take Mass as values are of the form '&lt;Number&gt; &lt;Mass unit of measure&gt;'. E.g., '7 kg'.
    MediaGallery: URIRef  # Web page type: Media gallery page. A mixed-media page that can contains media such as images, videos, and other multimedia.
    MediaObject: URIRef  # A media object, such as an image, video, or audio object embedded in a web page or a downloadable dataset i.e. DataDownload. Note that a creative work may have many media objects associated with it on the same web page. For example, a page about a single song (MusicRecording) may have a music video (VideoObject), and a high and low bandwidth audio stream (2 AudioObject's).
    MediaSubscription: URIRef  # A subscription which allows a user to access media including audio, video, books, etc.
    MedicalOrganization: URIRef  # A medical organization (physical or not), such as hospital, institution or clinic.
    MeetingRoom: URIRef  # A meeting room, conference room, or conference hall is a room provided for singular events such as business conferences and meetings (Source: Wikipedia, the free encyclopedia, see <a href="http://en.wikipedia.org/wiki/Conference_hall">http://en.wikipedia.org/wiki/Conference_hall</a>). <br /><br /> See also the <a href="/docs/hotels.html">dedicated document on the use of schema.org for marking up hotels and other forms of accommodations</a>.
    MensClothingStore: URIRef  # A men's clothing store.
    Menu: URIRef  # A structured representation of food or drink items available from a FoodEstablishment.
    MenuItem: URIRef  # A food or drink item listed in a menu or menu section.
    MenuSection: URIRef  # A sub-grouping of food or drink items in a menu. E.g. courses (such as 'Dinner', 'Breakfast', etc.), specific type of dishes (such as 'Meat', 'Vegan', 'Drinks', etc.), or some other classification made by the menu provider.
    Message: URIRef  # A single message from a sender to one or more organizations or people.
    MiddleSchool: URIRef  # A middle school (typically for children aged around 11-14, although this varies somewhat).
    MobileApplication: URIRef  # A software application designed specifically to work well on a mobile device such as a telephone.
    MobilePhoneStore: URIRef  # A store that sells mobile phones and related accessories.
    MonetaryAmount: URIRef  # A monetary value or range. This type can be used to describe an amount of money such as $50 USD, or a range as in describing a bank account being suitable for a balance between £1,000 and £1,000,000 GBP, or the value of a salary, etc. It is recommended to use <a class="localLink" href="http://schema.org/PriceSpecification">PriceSpecification</a> Types to describe the price of an Offer, Invoice, etc.
    MonetaryAmountDistribution: URIRef  # A statistical distribution of monetary amounts.
    Mosque: URIRef  # A mosque.
    Motel: URIRef  # A motel. <br /><br /> See also the <a href="/docs/hotels.html">dedicated document on the use of schema.org for marking up hotels and other forms of accommodations</a>.
    MotorcycleDealer: URIRef  # A motorcycle dealer.
    MotorcycleRepair: URIRef  # A motorcycle repair shop.
    Mountain: URIRef  # A mountain, like Mount Whitney or Mount Everest.
    MoveAction: URIRef  # The act of an agent relocating to a place.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/TransferAction">TransferAction</a>: Unlike TransferAction, the subject of the move is a living Person or Organization rather than an inanimate object.</li> </ul>
    Movie: URIRef  # A movie.
    MovieClip: URIRef  # A short segment/part of a movie.
    MovieRentalStore: URIRef  # A movie rental store.
    MovieSeries: URIRef  # A series of movies. Included movies can be indicated with the hasPart property.
    MovieTheater: URIRef  # A movie theater.
    MovingCompany: URIRef  # A moving company.
    Museum: URIRef  # A museum.
    MusicAlbum: URIRef  # A collection of music tracks.
    MusicAlbumProductionType: URIRef  # Classification of the album by it's type of content: soundtrack, live album, studio album, etc.
    MusicAlbumReleaseType: URIRef  # The kind of release which this album is: single, EP or album.
    MusicComposition: URIRef  # A musical composition.
    MusicEvent: URIRef  # Event type: Music event.
    MusicGroup: URIRef  # A musical group, such as a band, an orchestra, or a choir. Can also be a solo musician.
    MusicPlaylist: URIRef  # A collection of music tracks in playlist form.
    MusicRecording: URIRef  # A music recording (track), usually a single song.
    MusicRelease: URIRef  # A MusicRelease is a specific release of a music album.
    MusicReleaseFormatType: URIRef  # Format of this release (the type of recording media used, ie. compact disc, digital media, LP, etc.).
    MusicStore: URIRef  # A music store.
    MusicVenue: URIRef  # A music venue.
    MusicVideoObject: URIRef  # A music video file.
    NGO: URIRef  # Organization: Non-governmental Organization.
    NailSalon: URIRef  # A nail salon.
    NewsArticle: URIRef  # A NewsArticle is an article whose content reports news, or provides background context and supporting materials for understanding the news.<br/><br/>  A more detailed overview of <a href="/docs/news.html">schema.org News markup</a> is also available.
    NightClub: URIRef  # A nightclub or discotheque.
    Notary: URIRef  # A notary.
    NoteDigitalDocument: URIRef  # A file containing a note, primarily for the author.
    Number: URIRef  # Data type: Number.<br/><br/>  Usage guidelines:<br/><br/>  <ul> <li>Use values from 0123456789 (Unicode 'DIGIT ZERO' (U+0030) to 'DIGIT NINE' (U+0039)) rather than superficially similiar Unicode symbols.</li> <li>Use '.' (Unicode 'FULL STOP' (U+002E)) rather than ',' to indicate a decimal point. Avoid using these symbols as a readability separator.</li> </ul>
    NutritionInformation: URIRef  # Nutritional information about the recipe.
    Occupation: URIRef  # A profession, may involve prolonged training and/or a formal qualification.
    OceanBodyOfWater: URIRef  # An ocean (for example, the Pacific).
    Offer: URIRef  # An offer to transfer some rights to an item or to provide a service — for example, an offer to sell tickets to an event, to rent the DVD of a movie, to stream a TV show over the internet, to repair a motorcycle, or to loan a book.<br/><br/>  Note: As the <a class="localLink" href="http://schema.org/businessFunction">businessFunction</a> property, which identifies the form of offer (e.g. sell, lease, repair, dispose), defaults to http://purl.org/goodrelations/v1#Sell; an Offer without a defined businessFunction value can be assumed to be an offer to sell.<br/><br/>  For <a href="http://www.gs1.org/barcodes/technical/idkeys/gtin">GTIN</a>-related fields, see <a href="http://www.gs1.org/barcodes/support/check_digit_calculator">Check Digit calculator</a> and <a href="http://www.gs1us.org/resources/standards/gtin-validation-guide">validation guide</a> from <a href="http://www.gs1.org/">GS1</a>.
    OfferCatalog: URIRef  # An OfferCatalog is an ItemList that contains related Offers and/or further OfferCatalogs that are offeredBy the same provider.
    OfferItemCondition: URIRef  # A list of possible conditions for the item.
    OfficeEquipmentStore: URIRef  # An office equipment store.
    OnDemandEvent: URIRef  # A publication event e.g. catch-up TV or radio podcast, during which a program is available on-demand.
    OpeningHoursSpecification: URIRef  # A structured value providing information about the opening hours of a place or a certain service inside a place.<br/><br/>  The place is <strong>open</strong> if the <a class="localLink" href="http://schema.org/opens">opens</a> property is specified, and <strong>closed</strong> otherwise.<br/><br/>  If the value for the <a class="localLink" href="http://schema.org/closes">closes</a> property is less than the value for the <a class="localLink" href="http://schema.org/opens">opens</a> property then the hour range is assumed to span over the next day.
    Order: URIRef  # An order is a confirmation of a transaction (a receipt), which can contain multiple line items, each represented by an Offer that has been accepted by the customer.
    OrderAction: URIRef  # An agent orders an object/product/service to be delivered/sent.
    OrderItem: URIRef  # An order item is a line of an order. It includes the quantity and shipping details of a bought offer.
    OrderStatus: URIRef  # Enumerated status values for Order.
    Organization: URIRef  # An organization such as a school, NGO, corporation, club, etc.
    OrganizationRole: URIRef  # A subclass of Role used to describe roles within organizations.
    OrganizeAction: URIRef  # The act of manipulating/administering/supervising/controlling one or more objects.
    OutletStore: URIRef  # An outlet store.
    OwnershipInfo: URIRef  # A structured value providing information about when a certain organization or person owned a certain product.
    PaintAction: URIRef  # The act of producing a painting, typically with paint and canvas as instruments.
    Painting: URIRef  # A painting.
    ParcelDelivery: URIRef  # The delivery of a parcel either via the postal service or a commercial service.
    ParcelService: URIRef  # A private parcel service as the delivery mode available for a certain offer.<br/><br/>  Commonly used values:<br/><br/>  <ul> <li>http://purl.org/goodrelations/v1#DHL</li> <li>http://purl.org/goodrelations/v1#FederalExpress</li> <li>http://purl.org/goodrelations/v1#UPS</li> </ul>
    ParentAudience: URIRef  # A set of characteristics describing parents, who can be interested in viewing some content.
    Park: URIRef  # A park.
    ParkingFacility: URIRef  # A parking lot or other parking facility.
    PawnShop: URIRef  # A shop that will buy, or lend money against the security of, personal possessions.
    PayAction: URIRef  # An agent pays a price to a participant.
    PaymentCard: URIRef  # A payment method using a credit, debit, store or other card to associate the payment with an account.
    PaymentChargeSpecification: URIRef  # The costs of settling the payment using a particular payment method.
    PaymentMethod: URIRef  # A payment method is a standardized procedure for transferring the monetary amount for a purchase. Payment methods are characterized by the legal and technical structures used, and by the organization or group carrying out the transaction.<br/><br/>  Commonly used values:<br/><br/>  <ul> <li>http://purl.org/goodrelations/v1#ByBankTransferInAdvance</li> <li>http://purl.org/goodrelations/v1#ByInvoice</li> <li>http://purl.org/goodrelations/v1#Cash</li> <li>http://purl.org/goodrelations/v1#CheckInAdvance</li> <li>http://purl.org/goodrelations/v1#COD</li> <li>http://purl.org/goodrelations/v1#DirectDebit</li> <li>http://purl.org/goodrelations/v1#GoogleCheckout</li> <li>http://purl.org/goodrelations/v1#PayPal</li> <li>http://purl.org/goodrelations/v1#PaySwarm</li> </ul>
    PaymentService: URIRef  # A Service to transfer funds from a person or organization to a beneficiary person or organization.
    PaymentStatusType: URIRef  # A specific payment status. For example, PaymentDue, PaymentComplete, etc.
    PeopleAudience: URIRef  # A set of characteristics belonging to people, e.g. who compose an item's target audience.
    PerformAction: URIRef  # The act of participating in performance arts.
    PerformanceRole: URIRef  # A PerformanceRole is a Role that some entity places with regard to a theatrical performance, e.g. in a Movie, TVSeries etc.
    PerformingArtsTheater: URIRef  # A theater or other performing art center.
    PerformingGroup: URIRef  # A performance group, such as a band, an orchestra, or a circus.
    Periodical: URIRef  # A publication in any medium issued in successive parts bearing numerical or chronological designations and intended, such as a magazine, scholarly journal, or newspaper to continue indefinitely.<br/><br/>  See also <a href="http://blog.schema.org/2014/09/schemaorg-support-for-bibliographic_2.html">blog post</a>.
    Permit: URIRef  # A permit issued by an organization, e.g. a parking pass.
    Person: URIRef  # A person (alive, dead, undead, or fictional).
    PetStore: URIRef  # A pet store.
    Pharmacy: URIRef  # A pharmacy or drugstore.
    Photograph: URIRef  # A photograph.
    PhotographAction: URIRef  # The act of capturing still images of objects using a camera.
    Physician: URIRef  # A doctor's office.
    Place: URIRef  # Entities that have a somewhat fixed, physical extension.
    PlaceOfWorship: URIRef  # Place of worship, such as a church, synagogue, or mosque.
    PlanAction: URIRef  # The act of planning the execution of an event/task/action/reservation/plan to a future date.
    PlayAction: URIRef  # The act of playing/exercising/training/performing for enjoyment, leisure, recreation, Competition or exercise.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/ListenAction">ListenAction</a>: Unlike ListenAction (which is under ConsumeAction), PlayAction refers to performing for an audience or at an event, rather than consuming music.</li> <li><a class="localLink" href="http://schema.org/WatchAction">WatchAction</a>: Unlike WatchAction (which is under ConsumeAction), PlayAction refers to showing/displaying for an audience or at an event, rather than consuming visual content.</li> </ul>
    Playground: URIRef  # A playground.
    Plumber: URIRef  # A plumbing service.
    PoliceStation: URIRef  # A police station.
    Pond: URIRef  # A pond.
    PostOffice: URIRef  # A post office.
    PostalAddress: URIRef  # The mailing address.
    PreOrderAction: URIRef  # An agent orders a (not yet released) object/product/service to be delivered/sent.
    PrependAction: URIRef  # The act of inserting at the beginning if an ordered collection.
    Preschool: URIRef  # A preschool.
    PresentationDigitalDocument: URIRef  # A file containing slides or used for a presentation.
    PriceSpecification: URIRef  # A structured value representing a price or price range. Typically, only the subclasses of this type are used for markup. It is recommended to use <a class="localLink" href="http://schema.org/MonetaryAmount">MonetaryAmount</a> to describe independent amounts of money such as a salary, credit card limits, etc.
    Product: URIRef  # Any offered product or service. For example: a pair of shoes; a concert ticket; the rental of a car; a haircut; or an episode of a TV show streamed online.
    ProductModel: URIRef  # A datasheet or vendor specification of a product (in the sense of a prototypical description).
    ProfessionalService: URIRef  # Original definition: "provider of professional services."<br/><br/>  The general <a class="localLink" href="http://schema.org/ProfessionalService">ProfessionalService</a> type for local businesses was deprecated due to confusion with <a class="localLink" href="http://schema.org/Service">Service</a>. For reference, the types that it included were: <a class="localLink" href="http://schema.org/Dentist">Dentist</a>,         <a class="localLink" href="http://schema.org/AccountingService">AccountingService</a>, <a class="localLink" href="http://schema.org/Attorney">Attorney</a>, <a class="localLink" href="http://schema.org/Notary">Notary</a>, as well as types for several kinds of <a class="localLink" href="http://schema.org/HomeAndConstructionBusiness">HomeAndConstructionBusiness</a>: <a class="localLink" href="http://schema.org/Electrician">Electrician</a>, <a class="localLink" href="http://schema.org/GeneralContractor">GeneralContractor</a>,         <a class="localLink" href="http://schema.org/HousePainter">HousePainter</a>, <a class="localLink" href="http://schema.org/Locksmith">Locksmith</a>, <a class="localLink" href="http://schema.org/Plumber">Plumber</a>, <a class="localLink" href="http://schema.org/RoofingContractor">RoofingContractor</a>. <a class="localLink" href="http://schema.org/LegalService">LegalService</a> was introduced as a more inclusive supertype of <a class="localLink" href="http://schema.org/Attorney">Attorney</a>.
    ProfilePage: URIRef  # Web page type: Profile page.
    ProgramMembership: URIRef  # Used to describe membership in a loyalty programs (e.g. "StarAliance"), traveler clubs (e.g. "AAA"), purchase clubs ("Safeway Club"), etc.
    PropertyValue: URIRef  # A property-value pair, e.g. representing a feature of a product or place. Use the 'name' property for the name of the property. If there is an additional human-readable version of the value, put that into the 'description' property.<br/><br/>  Always use specific schema.org properties when a) they exist and b) you can populate them. Using PropertyValue as a substitute will typically not trigger the same effect as using the original, specific property.
    PropertyValueSpecification: URIRef  # A Property value specification.
    PublicSwimmingPool: URIRef  # A public swimming pool.
    PublicationEvent: URIRef  # A PublicationEvent corresponds indifferently to the event of publication for a CreativeWork of any type e.g. a broadcast event, an on-demand event, a book/journal publication via a variety of delivery media.
    PublicationIssue: URIRef  # A part of a successively published publication such as a periodical or publication volume, often numbered, usually containing a grouping of works such as articles.<br/><br/>  See also <a href="http://blog.schema.org/2014/09/schemaorg-support-for-bibliographic_2.html">blog post</a>.
    PublicationVolume: URIRef  # A part of a successively published publication such as a periodical or multi-volume work, often numbered. It may represent a time span, such as a year.<br/><br/>  See also <a href="http://blog.schema.org/2014/09/schemaorg-support-for-bibliographic_2.html">blog post</a>.
    QAPage: URIRef  # A QAPage is a WebPage focussed on a specific Question and its Answer(s), e.g. in a question answering site or documenting Frequently Asked Questions (FAQs).
    QualitativeValue: URIRef  # A predefined value for a product characteristic, e.g. the power cord plug type 'US' or the garment sizes 'S', 'M', 'L', and 'XL'.
    QuantitativeValue: URIRef  # A point value or interval for product characteristics and other purposes.
    QuantitativeValueDistribution: URIRef  # A statistical distribution of values.
    Quantity: URIRef  # Quantities such as distance, time, mass, weight, etc. Particular instances of say Mass are entities like '3 Kg' or '4 milligrams'.
    Question: URIRef  # A specific question - e.g. from a user seeking answers online, or collected in a Frequently Asked Questions (FAQ) document.
    QuoteAction: URIRef  # An agent quotes/estimates/appraises an object/product/service with a price at a location/store.
    RVPark: URIRef  # A place offering space for "Recreational Vehicles", Caravans, mobile homes and the like.
    RadioChannel: URIRef  # A unique instance of a radio BroadcastService on a CableOrSatelliteService lineup.
    RadioClip: URIRef  # A short radio program or a segment/part of a radio program.
    RadioEpisode: URIRef  # A radio episode which can be part of a series or season.
    RadioSeason: URIRef  # Season dedicated to radio broadcast and associated online delivery.
    RadioSeries: URIRef  # CreativeWorkSeries dedicated to radio broadcast and associated online delivery.
    RadioStation: URIRef  # A radio station.
    Rating: URIRef  # A rating is an evaluation on a numeric scale, such as 1 to 5 stars.
    ReactAction: URIRef  # The act of responding instinctively and emotionally to an object, expressing a sentiment.
    ReadAction: URIRef  # The act of consuming written content.
    RealEstateAgent: URIRef  # A real-estate agent.
    ReceiveAction: URIRef  # The act of physically/electronically taking delivery of an object thathas been transferred from an origin to a destination. Reciprocal of SendAction.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/SendAction">SendAction</a>: The reciprocal of ReceiveAction.</li> <li><a class="localLink" href="http://schema.org/TakeAction">TakeAction</a>: Unlike TakeAction, ReceiveAction does not imply that the ownership has been transfered (e.g. I can receive a package, but it does not mean the package is now mine).</li> </ul>
    Recipe: URIRef  # A recipe. For dietary restrictions covered by the recipe, a few common restrictions are enumerated via <a class="localLink" href="http://schema.org/suitableForDiet">suitableForDiet</a>. The <a class="localLink" href="http://schema.org/keywords">keywords</a> property can also be used to add more detail.
    RecyclingCenter: URIRef  # A recycling center.
    RegisterAction: URIRef  # The act of registering to be a user of a service, product or web page.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/JoinAction">JoinAction</a>: Unlike JoinAction, RegisterAction implies you are registering to be a user of a service, <em>not</em> a group/team of people.</li> <li>[FollowAction]]: Unlike FollowAction, RegisterAction doesn't imply that the agent is expecting to poll for updates from the object.</li> <li><a class="localLink" href="http://schema.org/SubscribeAction">SubscribeAction</a>: Unlike SubscribeAction, RegisterAction doesn't imply that the agent is expecting updates from the object.</li> </ul>
    RejectAction: URIRef  # The act of rejecting to/adopting an object.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/AcceptAction">AcceptAction</a>: The antonym of RejectAction.</li> </ul>
    RentAction: URIRef  # The act of giving money in return for temporary use, but not ownership, of an object such as a vehicle or property. For example, an agent rents a property from a landlord in exchange for a periodic payment.
    RentalCarReservation: URIRef  # A reservation for a rental car.<br/><br/>  Note: This type is for information about actual reservations, e.g. in confirmation emails or HTML pages with individual confirmations of reservations.
    ReplaceAction: URIRef  # The act of editing a recipient by replacing an old object with a new object.
    ReplyAction: URIRef  # The act of responding to a question/message asked/sent by the object. Related to <a class="localLink" href="http://schema.org/AskAction">AskAction</a><br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/AskAction">AskAction</a>: Appears generally as an origin of a ReplyAction.</li> </ul>
    Report: URIRef  # A Report generated by governmental or non-governmental organization.
    Reservation: URIRef  # Describes a reservation for travel, dining or an event. Some reservations require tickets. <br/><br/>  Note: This type is for information about actual reservations, e.g. in confirmation emails or HTML pages with individual confirmations of reservations. For offers of tickets, restaurant reservations, flights, or rental cars, use <a class="localLink" href="http://schema.org/Offer">Offer</a>.
    ReservationPackage: URIRef  # A group of multiple reservations with common values for all sub-reservations.
    ReservationStatusType: URIRef  # Enumerated status values for Reservation.
    ReserveAction: URIRef  # Reserving a concrete object.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/ScheduleAction">ScheduleAction</a></a>: Unlike ScheduleAction, ReserveAction reserves concrete objects (e.g. a table, a hotel) towards a time slot / spatial allocation.</li> </ul>
    Reservoir: URIRef  # A reservoir of water, typically an artificially created lake, like the Lake Kariba reservoir.
    Residence: URIRef  # The place where a person lives.
    Resort: URIRef  # A resort is a place used for relaxation or recreation, attracting visitors for holidays or vacations. Resorts are places, towns or sometimes commercial establishment operated by a single company (Source: Wikipedia, the free encyclopedia, see <a href="http://en.wikipedia.org/wiki/Resort">http://en.wikipedia.org/wiki/Resort</a>). <br /><br /> See also the <a href="/docs/hotels.html">dedicated document on the use of schema.org for marking up hotels and other forms of accommodations</a>.
    Restaurant: URIRef  # A restaurant.
    RestrictedDiet: URIRef  # A diet restricted to certain foods or preparations for cultural, religious, health or lifestyle reasons.
    ResumeAction: URIRef  # The act of resuming a device or application which was formerly paused (e.g. resume music playback or resume a timer).
    ReturnAction: URIRef  # The act of returning to the origin that which was previously received (concrete objects) or taken (ownership).
    Review: URIRef  # A review of an item - for example, of a restaurant, movie, or store.
    ReviewAction: URIRef  # The act of producing a balanced opinion about the object for an audience. An agent reviews an object with participants resulting in a review.
    RiverBodyOfWater: URIRef  # A river (for example, the broad majestic Shannon).
    Role: URIRef  # Represents additional information about a relationship or property. For example a Role can be used to say that a 'member' role linking some SportsTeam to a player occurred during a particular time period. Or that a Person's 'actor' role in a Movie was for some particular characterName. Such properties can be attached to a Role entity, which is then associated with the main entities using ordinary properties like 'member' or 'actor'.<br/><br/>  See also <a href="http://blog.schema.org/2014/06/introducing-role.html">blog post</a>.
    RoofingContractor: URIRef  # A roofing contractor.
    Room: URIRef  # A room is a distinguishable space within a structure, usually separated from other spaces by interior walls. (Source: Wikipedia, the free encyclopedia, see <a href="http://en.wikipedia.org/wiki/Room">http://en.wikipedia.org/wiki/Room</a>). <br /><br /> See also the <a href="/docs/hotels.html">dedicated document on the use of schema.org for marking up hotels and other forms of accommodations</a>.
    RsvpAction: URIRef  # The act of notifying an event organizer as to whether you expect to attend the event.
    RsvpResponseType: URIRef  # RsvpResponseType is an enumeration type whose instances represent responding to an RSVP request.
    SaleEvent: URIRef  # Event type: Sales event.
    ScheduleAction: URIRef  # Scheduling future actions, events, or tasks.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/ReserveAction">ReserveAction</a>: Unlike ReserveAction, ScheduleAction allocates future actions (e.g. an event, a task, etc) towards a time slot / spatial allocation.</li> </ul>
    ScholarlyArticle: URIRef  # A scholarly article.
    School: URIRef  # A school.
    ScreeningEvent: URIRef  # A screening of a movie or other video.
    Sculpture: URIRef  # A piece of sculpture.
    SeaBodyOfWater: URIRef  # A sea (for example, the Caspian sea).
    SearchAction: URIRef  # The act of searching for an object.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/FindAction">FindAction</a>: SearchAction generally leads to a FindAction, but not necessarily.</li> </ul>
    SearchResultsPage: URIRef  # Web page type: Search results page.
    Season: URIRef  # A media season e.g. tv, radio, video game etc.
    Seat: URIRef  # Used to describe a seat, such as a reserved seat in an event reservation.
    SelfStorage: URIRef  # A self-storage facility.
    SellAction: URIRef  # The act of taking money from a buyer in exchange for goods or services rendered. An agent sells an object, product, or service to a buyer for a price. Reciprocal of BuyAction.
    SendAction: URIRef  # The act of physically/electronically dispatching an object for transfer from an origin to a destination.Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/ReceiveAction">ReceiveAction</a>: The reciprocal of SendAction.</li> <li><a class="localLink" href="http://schema.org/GiveAction">GiveAction</a>: Unlike GiveAction, SendAction does not imply the transfer of ownership (e.g. I can send you my laptop, but I'm not necessarily giving it to you).</li> </ul>
    Series: URIRef  # A Series in schema.org is a group of related items, typically but not necessarily of the same kind. See also <a class="localLink" href="http://schema.org/CreativeWorkSeries">CreativeWorkSeries</a>, <a class="localLink" href="http://schema.org/EventSeries">EventSeries</a>.
    Service: URIRef  # A service provided by an organization, e.g. delivery service, print services, etc.
    ServiceChannel: URIRef  # A means for accessing a service, e.g. a government office location, web site, or phone number.
    ShareAction: URIRef  # The act of distributing content to people for their amusement or edification.
    ShoeStore: URIRef  # A shoe store.
    ShoppingCenter: URIRef  # A shopping center or mall.
    SingleFamilyResidence: URIRef  # Residence type: Single-family home.
    SiteNavigationElement: URIRef  # A navigation element of the page.
    SkiResort: URIRef  # A ski resort.
    SocialEvent: URIRef  # Event type: Social event.
    SocialMediaPosting: URIRef  # A post to a social media platform, including blog posts, tweets, Facebook posts, etc.
    SoftwareApplication: URIRef  # A software application.
    SoftwareSourceCode: URIRef  # Computer programming source code. Example: Full (compile ready) solutions, code snippet samples, scripts, templates.
    SomeProducts: URIRef  # A placeholder for multiple similar products of the same kind.
    SpeakableSpecification: URIRef  # A SpeakableSpecification indicates (typically via <a class="localLink" href="http://schema.org/xpath">xpath</a> or <a class="localLink" href="http://schema.org/cssSelector">cssSelector</a>) sections of a document that are highlighted as particularly <a class="localLink" href="http://schema.org/speakable">speakable</a>. Instances of this type are expected to be used primarily as values of the <a class="localLink" href="http://schema.org/speakable">speakable</a> property.
    Specialty: URIRef  # Any branch of a field in which people typically develop specific expertise, usually after significant study, time, and effort.
    SportingGoodsStore: URIRef  # A sporting goods store.
    SportsActivityLocation: URIRef  # A sports location, such as a playing field.
    SportsClub: URIRef  # A sports club.
    SportsEvent: URIRef  # Event type: Sports event.
    SportsOrganization: URIRef  # Represents the collection of all sports organizations, including sports teams, governing bodies, and sports associations.
    SportsTeam: URIRef  # Organization: Sports team.
    SpreadsheetDigitalDocument: URIRef  # A spreadsheet file.
    StadiumOrArena: URIRef  # A stadium.
    State: URIRef  # A state or province of a country.
    SteeringPositionValue: URIRef  # A value indicating a steering position.
    Store: URIRef  # A retail good store.
    StructuredValue: URIRef  # Structured values are used when the value of a property has a more complex structure than simply being a textual value or a reference to another thing.
    SubscribeAction: URIRef  # The act of forming a personal connection with someone/something (object) unidirectionally/asymmetrically to get updates pushed to.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/FollowAction">FollowAction</a>: Unlike FollowAction, SubscribeAction implies that the subscriber acts as a passive agent being constantly/actively pushed for updates.</li> <li><a class="localLink" href="http://schema.org/RegisterAction">RegisterAction</a>: Unlike RegisterAction, SubscribeAction implies that the agent is interested in continuing receiving updates from the object.</li> <li><a class="localLink" href="http://schema.org/JoinAction">JoinAction</a>: Unlike JoinAction, SubscribeAction implies that the agent is interested in continuing receiving updates from the object.</li> </ul>
    SubwayStation: URIRef  # A subway station.
    Suite: URIRef  # A suite in a hotel or other public accommodation, denotes a class of luxury accommodations, the key feature of which is multiple rooms (Source: Wikipedia, the free encyclopedia, see <a href="http://en.wikipedia.org/wiki/Suite_(hotel)">http://en.wikipedia.org/wiki/Suite_(hotel)</a>). <br /><br /> See also the <a href="/docs/hotels.html">dedicated document on the use of schema.org for marking up hotels and other forms of accommodations</a>.
    SuspendAction: URIRef  # The act of momentarily pausing a device or application (e.g. pause music playback or pause a timer).
    Synagogue: URIRef  # A synagogue.
    TVClip: URIRef  # A short TV program or a segment/part of a TV program.
    TVEpisode: URIRef  # A TV episode which can be part of a series or season.
    TVSeason: URIRef  # Season dedicated to TV broadcast and associated online delivery.
    TVSeries: URIRef  # CreativeWorkSeries dedicated to TV broadcast and associated online delivery.
    Table: URIRef  # A table on a Web page.
    TakeAction: URIRef  # The act of gaining ownership of an object from an origin. Reciprocal of GiveAction.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/GiveAction">GiveAction</a>: The reciprocal of TakeAction.</li> <li><a class="localLink" href="http://schema.org/ReceiveAction">ReceiveAction</a>: Unlike ReceiveAction, TakeAction implies that ownership has been transfered.</li> </ul>
    TattooParlor: URIRef  # A tattoo parlor.
    Taxi: URIRef  # A taxi.
    TaxiReservation: URIRef  # A reservation for a taxi.<br/><br/>  Note: This type is for information about actual reservations, e.g. in confirmation emails or HTML pages with individual confirmations of reservations. For offers of tickets, use <a class="localLink" href="http://schema.org/Offer">Offer</a>.
    TaxiService: URIRef  # A service for a vehicle for hire with a driver for local travel. Fares are usually calculated based on distance traveled.
    TaxiStand: URIRef  # A taxi stand.
    TechArticle: URIRef  # A technical article - Example: How-to (task) topics, step-by-step, procedural troubleshooting, specifications, etc.
    TelevisionChannel: URIRef  # A unique instance of a television BroadcastService on a CableOrSatelliteService lineup.
    TelevisionStation: URIRef  # A television station.
    TennisComplex: URIRef  # A tennis complex.
    Text: URIRef  # Data type: Text.
    TextDigitalDocument: URIRef  # A file composed primarily of text.
    TheaterEvent: URIRef  # Event type: Theater performance.
    TheaterGroup: URIRef  # A theater group or company, for example, the Royal Shakespeare Company or Druid Theatre.
    Thing: URIRef  # The most generic type of item.
    Ticket: URIRef  # Used to describe a ticket to an event, a flight, a bus ride, etc.
    TieAction: URIRef  # The act of reaching a draw in a competitive activity.
    Time: URIRef  # A point in time recurring on multiple days in the form hh:mm:ss[Z|(+|-)hh:mm] (see <a href="http://www.w3.org/TR/xmlschema-2/#time">XML schema for details</a>).
    TipAction: URIRef  # The act of giving money voluntarily to a beneficiary in recognition of services rendered.
    TireShop: URIRef  # A tire shop.
    TouristAttraction: URIRef  # A tourist attraction.  In principle any Thing can be a <a class="localLink" href="http://schema.org/TouristAttraction">TouristAttraction</a>, from a <a class="localLink" href="http://schema.org/Mountain">Mountain</a> and <a class="localLink" href="http://schema.org/LandmarksOrHistoricalBuildings">LandmarksOrHistoricalBuildings</a> to a <a class="localLink" href="http://schema.org/LocalBusiness">LocalBusiness</a>.  This Type can be used on its own to describe a general <a class="localLink" href="http://schema.org/TouristAttraction">TouristAttraction</a>, or be used as an <a class="localLink" href="http://schema.org/additionalType">additionalType</a> to add tourist attraction properties to any other type.  (See examples below)
    TouristInformationCenter: URIRef  # A tourist information center.
    ToyStore: URIRef  # A toy store.
    TrackAction: URIRef  # An agent tracks an object for updates.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/FollowAction">FollowAction</a>: Unlike FollowAction, TrackAction refers to the interest on the location of innanimates objects.</li> <li><a class="localLink" href="http://schema.org/SubscribeAction">SubscribeAction</a>: Unlike SubscribeAction, TrackAction refers to  the interest on the location of innanimate objects.</li> </ul>
    TradeAction: URIRef  # The act of participating in an exchange of goods and services for monetary compensation. An agent trades an object, product or service with a participant in exchange for a one time or periodic payment.
    TrainReservation: URIRef  # A reservation for train travel.<br/><br/>  Note: This type is for information about actual reservations, e.g. in confirmation emails or HTML pages with individual confirmations of reservations. For offers of tickets, use <a class="localLink" href="http://schema.org/Offer">Offer</a>.
    TrainStation: URIRef  # A train station.
    TrainTrip: URIRef  # A trip on a commercial train line.
    TransferAction: URIRef  # The act of transferring/moving (abstract or concrete) animate or inanimate objects from one place to another.
    TravelAction: URIRef  # The act of traveling from an fromLocation to a destination by a specified mode of transport, optionally with participants.
    TravelAgency: URIRef  # A travel agency.
    Trip: URIRef  # A trip or journey. An itinerary of visits to one or more places.
    TypeAndQuantityNode: URIRef  # A structured value indicating the quantity, unit of measurement, and business function of goods included in a bundle offer.
    URL: URIRef  # Data type: URL.
    UnRegisterAction: URIRef  # The act of un-registering from a service.<br/><br/>  Related actions:<br/><br/>  <ul> <li><a class="localLink" href="http://schema.org/RegisterAction">RegisterAction</a>: antonym of UnRegisterAction.</li> <li><a class="localLink" href="http://schema.org/LeaveAction">LeaveAction</a>: Unlike LeaveAction, UnRegisterAction implies that you are unregistering from a service you werer previously registered, rather than leaving a team/group of people.</li> </ul>
    UnitPriceSpecification: URIRef  # The price asked for a given offer by the respective organization or person.
    UpdateAction: URIRef  # The act of managing by changing/editing the state of the object.
    UseAction: URIRef  # The act of applying an object to its intended purpose.
    UserBlocks: URIRef  # UserInteraction and its subtypes is an old way of talking about users interacting with pages. It is generally better to use <a class="localLink" href="http://schema.org/Action">Action</a>-based vocabulary, alongside types such as <a class="localLink" href="http://schema.org/Comment">Comment</a>.
    UserCheckins: URIRef  # UserInteraction and its subtypes is an old way of talking about users interacting with pages. It is generally better to use <a class="localLink" href="http://schema.org/Action">Action</a>-based vocabulary, alongside types such as <a class="localLink" href="http://schema.org/Comment">Comment</a>.
    UserComments: URIRef  # UserInteraction and its subtypes is an old way of talking about users interacting with pages. It is generally better to use <a class="localLink" href="http://schema.org/Action">Action</a>-based vocabulary, alongside types such as <a class="localLink" href="http://schema.org/Comment">Comment</a>.
    UserDownloads: URIRef  # UserInteraction and its subtypes is an old way of talking about users interacting with pages. It is generally better to use <a class="localLink" href="http://schema.org/Action">Action</a>-based vocabulary, alongside types such as <a class="localLink" href="http://schema.org/Comment">Comment</a>.
    UserInteraction: URIRef  # UserInteraction and its subtypes is an old way of talking about users interacting with pages. It is generally better to use <a class="localLink" href="http://schema.org/Action">Action</a>-based vocabulary, alongside types such as <a class="localLink" href="http://schema.org/Comment">Comment</a>.
    UserLikes: URIRef  # UserInteraction and its subtypes is an old way of talking about users interacting with pages. It is generally better to use <a class="localLink" href="http://schema.org/Action">Action</a>-based vocabulary, alongside types such as <a class="localLink" href="http://schema.org/Comment">Comment</a>.
    UserPageVisits: URIRef  # UserInteraction and its subtypes is an old way of talking about users interacting with pages. It is generally better to use <a class="localLink" href="http://schema.org/Action">Action</a>-based vocabulary, alongside types such as <a class="localLink" href="http://schema.org/Comment">Comment</a>.
    UserPlays: URIRef  # UserInteraction and its subtypes is an old way of talking about users interacting with pages. It is generally better to use <a class="localLink" href="http://schema.org/Action">Action</a>-based vocabulary, alongside types such as <a class="localLink" href="http://schema.org/Comment">Comment</a>.
    UserPlusOnes: URIRef  # UserInteraction and its subtypes is an old way of talking about users interacting with pages. It is generally better to use <a class="localLink" href="http://schema.org/Action">Action</a>-based vocabulary, alongside types such as <a class="localLink" href="http://schema.org/Comment">Comment</a>.
    UserTweets: URIRef  # UserInteraction and its subtypes is an old way of talking about users interacting with pages. It is generally better to use <a class="localLink" href="http://schema.org/Action">Action</a>-based vocabulary, alongside types such as <a class="localLink" href="http://schema.org/Comment">Comment</a>.
    Vehicle: URIRef  # A vehicle is a device that is designed or used to transport people or cargo over land, water, air, or through space.
    VideoGallery: URIRef  # Web page type: Video gallery page.
    VideoGame: URIRef  # A video game is an electronic game that involves human interaction with a user interface to generate visual feedback on a video device.
    VideoGameClip: URIRef  # A short segment/part of a video game.
    VideoGameSeries: URIRef  # A video game series.
    VideoObject: URIRef  # A video file.
    ViewAction: URIRef  # The act of consuming static visual content.
    VisualArtsEvent: URIRef  # Event type: Visual arts event.
    VisualArtwork: URIRef  # A work of art that is primarily visual in character.
    Volcano: URIRef  # A volcano, like Fuji san.
    VoteAction: URIRef  # The act of expressing a preference from a fixed/finite/structured set of choices/options.
    WPAdBlock: URIRef  # An advertising section of the page.
    WPFooter: URIRef  # The footer section of the page.
    WPHeader: URIRef  # The header section of the page.
    WPSideBar: URIRef  # A sidebar section of the page.
    WantAction: URIRef  # The act of expressing a desire about the object. An agent wants an object.
    WarrantyPromise: URIRef  # A structured value representing the duration and scope of services that will be provided to a customer free of charge in case of a defect or malfunction of a product.
    WarrantyScope: URIRef  # A range of of services that will be provided to a customer free of charge in case of a defect or malfunction of a product.<br/><br/>  Commonly used values:<br/><br/>  <ul> <li>http://purl.org/goodrelations/v1#Labor-BringIn</li> <li>http://purl.org/goodrelations/v1#PartsAndLabor-BringIn</li> <li>http://purl.org/goodrelations/v1#PartsAndLabor-PickUp</li> </ul>
    WatchAction: URIRef  # The act of consuming dynamic/moving visual content.
    Waterfall: URIRef  # A waterfall, like Niagara.
    WearAction: URIRef  # The act of dressing oneself in clothing.
    WebApplication: URIRef  # Web applications.
    WebPage: URIRef  # A web page. Every web page is implicitly assumed to be declared to be of type WebPage, so the various properties about that webpage, such as <code>breadcrumb</code> may be used. We recommend explicit declaration if these properties are specified, but if they are found outside of an itemscope, they will be assumed to be about the page.
    WebPageElement: URIRef  # A web page element, like a table or an image.
    WebSite: URIRef  # A WebSite is a set of related web pages and other items typically served from a single web domain and accessible via URLs.
    WholesaleStore: URIRef  # A wholesale store.
    WinAction: URIRef  # The act of achieving victory in a competitive activity.
    Winery: URIRef  # A winery.
    WorkersUnion: URIRef  # A Workers Union (also known as a Labor Union, Labour Union, or Trade Union) is an organization that promotes the interests of its worker members by collectively bargaining with management, organizing, and political lobbying.
    WriteAction: URIRef  # The act of authoring written creative content.
    Zoo: URIRef  # A zoo.

    # Valid non-python identifiers
    _extras = ["False", "True", "yield"]

    _NS = Namespace("http://schema.org/")
