DATA_BASE = 'chinook.db'
ALL_TABLES_QUERY = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"

tablesCreationSQL = {  # THIS DICTIONARY IS TO CREATE THE TABLES FROM THE CSV FILE!!!!
	"playlists": f"""
        CREATE TABLE IF NOT EXISTS playlists (
            PlaylistId INTEGER,Name NVARCHAR(120),
            PRIMARY KEY(PlaylistId)
        );
        """,
	
	"artists": f"""
        CREATE TABLE IF NOT EXISTS artists (
            ArtistId INTEGER,
            Name NVARCHAR(120),
            PRIMARY KEY(ArtistId)
        );""",
	
	"media_types": f"""
        CREATE TABLE IF NOT EXISTS media_types (
            MediaTypeId INTEGER,
            Name NVARCHAR(120),
            PRIMARY KEY(MediaTypeId)
        );""",
	
	"genres": f"""
        CREATE TABLE IF NOT EXISTS genres (
            GenreId INTEGER,
            Name NVARCHAR(120),
            PRIMARY KEY(GenreId)
        );""",
	
	"employees": f"""
        CREATE TABLE IF NOT EXISTS employees (
            EmployeeId INTEGER,
            LastName NVARCHAR(20),
            FirstName NVARCHAR(20),
            Title NVARCHAR(30),
            ReportsTo INTEGER,
            BirthDate DATETIME,
            HireDate DATETIME,
            Address NVARCHAR(70),
            City NVARCHAR(40),
            State NVARCHAR(40),
            Country NVARCHAR(40),
            PostalCode NVARCHAR(10),
            Phone NVARCHAR(24),
            Fax NVARCHAR(24),
            Email NVARCHAR(60),
            PRIMARY KEY(EmployeeId)
            );""",
	
	"invoices": f"""
        CREATE TABLE IF NOT EXISTS invoices (
            InvoiceId INTEGER,
            CustomerId INTEGER,
            InvoiceDate DATETIME,
            BillingAddress NVARCHAR(70),
            BillingCity NVARCHAR(40),
            BillingState NVARCHAR(40),
            BillingCountry NVARCHAR(40),
            BillingPostalCode NVARCHAR(10),
            Total REAL,
            PRIMARY KEY(InvoiceId),
            FOREIGN KEY (CustomerId)
                references customers(CustomerId)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );""",
	
	"customers": f"""
        CREATE TABLE IF NOT EXISTS customers (
            CustomerId INTEGER,
            FirstName NVARCHAR(40),
            LastName NVARCHAR(20),
            Company NVARCHAR(80),
            Address NVARCHAR(70),
            City NVARCHAR(40),
            State NVARCHAR(40),
            Country NVARCHAR(40),
            PostalCode NVARCHAR(10),
            Phone NVARCHAR(24),
            Fax NVARCHAR(24),
            Email NVARCHAR(60),
            SupportRepId INTEGER,
            PRIMARY KEY(CustomerId),
            FOREIGN KEY (SupportRepId)
                references employees(EmployeeId)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
            """,
	
	"albums": f"""
        CREATE TABLE IF NOT EXISTS albums (
            AlbumId INTEGER,
            Title NVARCHAR(160),
            ArtistId INTEGER,
            PRIMARY KEY(AlbumId),
            FOREIGN KEY (ArtistId)
                references artists(ArtistId)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );""",
	
	"tracks": f"""
        CREATE TABLE IF NOT EXISTS tracks (
            TrackId INTEGER,
            Name NVARCHAR(200),
            AlbumId INTEGER,
            MediaTypeId INTEGER,
            GenreId INTEGER,
            Composer NVARCHAR(220),
            Milliseconds INTEGER,
            Bytes INTEGER,
            UnitPrice REAL,
            PRIMARY KEY(TrackId),
            FOREIGN KEY (AlbumId)
                references albums(AlbumId)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,

            FOREIGN KEY (MediaTypeId)
                references media_types(MediaTypeId)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,

            FOREIGN KEY (GenreId)
                references genres(GenreId)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );""",
	
	"playlist_track": f"""
        CREATE TABLE IF NOT EXISTS playlist_track (
            PlaylistId INTEGER,
            TrackId INTEGER,
            PRIMARY KEY(PlaylistId, TrackId),
            FOREIGN KEY (PlaylistId)
                references playlists(PlaylistId)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
            FOREIGN KEY (TrackId)
                references tracks(TrackId)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );""",
	
	"invoice_items": f"""
        CREATE TABLE IF NOT EXISTS invoice_items (
            InvoiceLineId INTEGER,
            InvoiceId INTEGER,
            TrackId INTEGER,
            UnitPrice REAL,
            Quantity INTEGER,
            PRIMARY KEY(InvoiceLineId),
            FOREIGN KEY (InvoiceId)
                references invoices(InvoiceId)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
            FOREIGN KEY (TrackId)
                references tracks(TrackId)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );""",
	
}

tablesWhereSQL = {
	"playlists": f"PlaylistId",
	"artists": f"ArtistId",
	"media_types": f"MediaTypeId",
	"genres": f"GenreId",
	"employees": f"EmployeeId",
	"invoices": f"InvoiceId",
	"customers": f"CustomerId",
	"albums": f"AlbumId",
	"tracks": f"TrackId",
	"playlist_track": f"PlaylistId TrackId",
	"invoice_items": f"InvoiceLineId",
}