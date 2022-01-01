DATA_BASE = 'chinook.db'
ALL_TABLES_QUERY = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
BUTTON_PADX = 10

quotes_check_dict = {
	"genres": "CREATE TABLE IF NOT EXISTS genres (GenreId INTEGER,Name NVARCHAR(120), PRIMARY KEY(GenreId));",
	"employees": "CREATE TABLE IF NOT EXISTS employees (EmployeeId INTEGER,LastName NVARCHAR(20),FirstName NVARCHAR(20),Title NVARCHAR(30),ReportsTo INTEGER,BirthDate DATETIME,HireDate DATETIME,Address NVARCHAR(70),City NVARCHAR(40),State NVARCHAR(40),Country NVARCHAR(40),PostalCode NVARCHAR(10),Phone NVARCHAR(24),Fax NVARCHAR(24),Email NVARCHAR(60), PRIMARY KEY(EmployeeId));",
	"tracks": "CREATE TABLE IF NOT EXISTS tracks (TrackId INTEGER,Name NVARCHAR(200),AlbumId INTEGER,MediaTypeId INTEGER,GenreId INTEGER,Composer NVARCHAR(220),Milliseconds INTEGER,Bytes INTEGER,UnitPrice REAL, FOREIGN KEY (AlbumId) references albums(AlbumId), FOREIGN KEY (MediaTypeId) references media_types(MediaTypeId), FOREIGN KEY (GenreId) references genres(GenreId), PRIMARY KEY(TrackId));",
	"invoices": "CREATE TABLE IF NOT EXISTS invoices (InvoiceId INTEGER,CustomerId INTEGER,InvoiceDate DATETIME,BillingAddress NVARCHAR(70),BillingCity NVARCHAR(40),BillingState NVARCHAR(40),BillingCountry NVARCHAR(40),BillingPostalCode NVARCHAR(10),Total REAL, PRIMARY KEY(InvoiceId));",
	"customers": "CREATE TABLE IF NOT EXISTS customers (CustomerId INTEGER,FirstName NVARCHAR(40),LastName NVARCHAR(20),Company NVARCHAR(80),Address NVARCHAR(70),City NVARCHAR(40),State NVARCHAR(40),Country NVARCHAR(40),PostalCode NVARCHAR(10),Phone NVARCHAR(24),Fax NVARCHAR(24),Email NVARCHAR(60),SupportRepId INTEGER, FOREIGN KEY (SupportRepId) references employees(EmployeeId), PRIMARY KEY(CustomerId));",
	"albums": "CREATE TABLE IF NOT EXISTS albums (AlbumId INTEGER,Title NVARCHAR(160),ArtistId INTEGER, FOREIGN KEY (artistId) references artists(ArtistId), PRIMARY KEY(AlbumId));",
	"playlist_track": "CREATE TABLE IF NOT EXISTS playlist_track (PlaylistId INTEGER,TrackId INTEGER, FOREIGN KEY (PlaylistId) references playlists(PlaylistId), FOREIGN KEY (TrackId) references tracks(TrackId) PRIMARY KEY(PlaylistId, TrackId));",
	"invoice_items": "CREATE TABLE IF NOT EXISTS invoice_items (InvoiceLineId INTEGER,InvoiceId INTEGER,TrackId INTEGER,UnitPrice REAL,Quantity INTEGER, FOREIGN KEY (InvoiceId) references invoices(InvoiceId), FOREIGN KEY (TrackId) references tracks(TrackId), PRIMARY KEY(InvoiceLineId));",
	"playlists": "CREATE TABLE IF NOT EXISTS playlists (PlaylistId INTEGER,Name NVARCHAR(120), PRIMARY KEY(PlaylistId));",
	"artists": "CREATE TABLE IF NOT EXISTS artists (ArtistId INTEGER,Name NVARCHAR(120), PRIMARY KEY(ArtistId));",
	"media_types": "CREATE TABLE IF NOT EXISTS media_types (MediaTypeId INTEGER,Name NVARCHAR(120), PRIMARY KEY(MediaTypeId));",
}

primary_key_dict = {
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


error_messages = {
	"empty_table": "Table Has No Columns!",
	"no_tbl_selected":"In order to drop a table, you need to select a table first",
	"row_dlt_no_tbl":"In order to delete a row, you need to select a table first",
	"no_row_selected":"In order to drop a row, you need to select a table first",
	"uncheck_before_insret":"Please un-check selected row before inserting a new row",
	"row_add_no_tbl":"In order to add a row, you need to select a table first",
	"db_connection" : "Couldn't connect to database: ",
	"wrong_id_dlt" : "Not sufficient id's. An INTEGER is needed, or List with 2 ids",
	"row_dlt_err": "Could not delete row with primary key",
	"duplicate_ids": "This id (Primary Key) already exists. Primary key must be unique",
	"invalid_input": "Invalid input. Make sure you entered a valid TYPE",
	"disonnect_err" : "Couldn't disconnect from database - ",
	"drop_tbl_err" : "Couldn't drop table",
	"pk_update" : "Primary Keys are unchangable"
}

success_messages = {
	"edit_completed":"Edit Completed Successfully",
	"clear_db": "Cleared DB Successfully",
	"drop_tbl":"Dropped Table Successfully",
	"delete_row":"Deleted Row Successfully",
	"row_insert":"Row Inserted Successfully"
}

warning_messages = {
	"drop_tbl_warning":"Are you sure you want to drop this table ?",
	"drop_db_warning":"All tables will be deleted.\nAre you sure you want to drop the database?",
	"row_delete_warning":"Are you sure you want to delete the selected row?"
}