DATA_BASE = 'chinook.db'
ALL_TABLES_QUERY = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
BUTTON_PADX = 10

tablesCreationSQL = {
	"playlists": f"CREATE TABLE IF NOT EXISTS playlists (PlaylistId INTEGER,Name NVARCHAR(120), PRIMARY KEY(PlaylistId));",
	"artists": f"CREATE TABLE IF NOT EXISTS artists (ArtistId INTEGER,Name NVARCHAR(120), PRIMARY KEY(ArtistId));",
	"media_types": f"CREATE TABLE IF NOT EXISTS media_types (MediaTypeId INTEGER,Name NVARCHAR(120), PRIMARY KEY(MediaTypeId));",
	"genres": f"CREATE TABLE IF NOT EXISTS genres (GenreId INTEGER,Name NVARCHAR(120), PRIMARY KEY(GenreId));",
	"employees": f"CREATE TABLE IF NOT EXISTS employees (EmployeeId INTEGER,LastName NVARCHAR(20),FirstName NVARCHAR(20),Title NVARCHAR(30),ReportsTo INTEGER,BirthDate DATETIME,HireDate DATETIME,Address NVARCHAR(70),City NVARCHAR(40),State NVARCHAR(40),Country NVARCHAR(40),PostalCode NVARCHAR(10),Phone NVARCHAR(24),Fax NVARCHAR(24),Email NVARCHAR(60), PRIMARY KEY(EmployeeId));",
	"invoices": f"CREATE TABLE IF NOT EXISTS invoices (InvoiceId INTEGER,CustomerId INTEGER,InvoiceDate DATETIME,BillingAddress NVARCHAR(70),BillingCity NVARCHAR(40),BillingState NVARCHAR(40),BillingCountry NVARCHAR(40),BillingPostalCode NVARCHAR(10),Total REAL, PRIMARY KEY(InvoiceId));",
	"customers": f"CREATE TABLE IF NOT EXISTS customers (CustomerId INTEGER,FirstName NVARCHAR(40),LastName NVARCHAR(20),Company NVARCHAR(80),Address NVARCHAR(70),City NVARCHAR(40),State NVARCHAR(40),Country NVARCHAR(40),PostalCode NVARCHAR(10),Phone NVARCHAR(24),Fax NVARCHAR(24),Email NVARCHAR(60),SupportRepId INTEGER, FOREIGN KEY (SupportRepId) references employees(EmployeeId), PRIMARY KEY(CustomerId));",
	"albums": f"CREATE TABLE IF NOT EXISTS albums (AlbumId INTEGER,Title NVARCHAR(160),ArtistId INTEGER, FOREIGN KEY (artistId) references artists(ArtistId), PRIMARY KEY(AlbumId));",
	"tracks": f"CREATE TABLE IF NOT EXISTS tracks (TrackId INTEGER,Name NVARCHAR(200),AlbumId INTEGER,MediaTypeId INTEGER,GenreId INTEGER,Composer NVARCHAR(220),Milliseconds INTEGER,Bytes INTEGER,UnitPrice REAL, FOREIGN KEY (AlbumId) references albums(AlbumId), FOREIGN KEY (MediaTypeId) references media_types(MediaTypeId), FOREIGN KEY (GenreId) references genres(GenreId), PRIMARY KEY(TrackId));",
	"playlist_track": f"CREATE TABLE IF NOT EXISTS playlist_track (PlaylistId INTEGER,TrackId INTEGER, FOREIGN KEY (PlaylistId) references playlists(PlaylistId), FOREIGN KEY (TrackId) references tracks(TrackId) PRIMARY KEY(PlaylistId, TrackId));",
	"invoice_items": f"CREATE TABLE IF NOT EXISTS invoice_items (InvoiceLineId INTEGER,InvoiceId INTEGER,TrackId INTEGER,UnitPrice REAL,Quantity INTEGER, FOREIGN KEY (InvoiceId) references invoices(InvoiceId), FOREIGN KEY (TrackId) references tracks(TrackId), PRIMARY KEY(InvoiceLineId));",
}

tables_where_SQL = {
	"customers": "CustomerId",
	"playlists": "PlaylistId",
	"artists": "ArtistId",
	"media_types": "MediaTypeId",
	"genres": "GenreId",
	"employees": "EmployeeId",
	"invoices": "InvoiceId CustomerId",
	"albums": "AlbumId",
	"tracks": "TrackId",
	"playlist_track": "PlaylistId TrackId",
	"invoice_items": "InvoiceLineId",
}