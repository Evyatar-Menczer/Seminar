import sqlite3
import csv
from sqlite3 import Error


class sqlManager():
    tablesCreationSQL = { # THIS DICTIONARY IS TO CREATE THE TABLES FROM THE CSV FILE!!!!
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

    def __init__(self, db_file) -> None:
        """Initialize class object and establishing connection to the DB file.

        Args:
            db_file (str): DB file location

        Raises:
            Error: Could not initialize a database connection from db_file
        """
        try:
            self.conn = sqlite3.connect(db_file)
            self.cursor = self.conn.cursor()
            # self.cursor.execute("PRAGMA foreign_keys = ON")
        except Error as e:
            raise Error(f"Could not initialize a database connection from file {db_file} - ", e)

    def createDatabaseFromCSV(self):
        """Imports information from various predetermined CSV files into our connected DB file.

        Raises:
            ValueError: Could not import information to our DB file from the predetermined CSV files.
        """
        try:
            for k in sqlManager.tablesCreationSQL.keys():
                self.createTable(k)
            self.conn.commit()
        except Error as e:
            raise ValueError(f"Could not create database from predetermined CSV files - ", e)

    def clear(self):
        """Clears our DB file.

        Raises:
            ValueError: Could not clear our DB file.
        """
        try:
            for k in sqlManager.tablesCreationSQL.keys():
                self.cursor.execute(f"DROP TABLE IF EXISTS {k}")
            self.conn.commit()
        except Error as e:
            raise ValueError(f"Could not clear the database - ", e)

    def dropTable(self, tableName):
        """Drop the table {tableName} from our DB.

        Args:
            tableName (str): The name of the table that we wish to drop.

        Raises:
            ValueError: In case the table wasn't found or any other reason the table couldn't have been dropped.
        """
        try:
            self.cursor.execute(f"DROP TABLE IF EXISTS {tableName}")
            self.conn.commit()
        except Error as e:
            raise ValueError(f"Could not drop table {tableName} - ", e)

    def createTable(self, tableFromDict):
        """Create the table {tableFromDict} into our DB.

        Args:
            tableFromDict (str): The name of the table that we wish to create.

        Raises:
            ValueError: {tableFromDict} is not one of the predetermined tables.
            Exception: {tableFromDict} couldn't have been created.
        """
        try:
            if tableFromDict not in sqlManager.tablesCreationSQL.keys():
                raise ValueError('Only predetermined tables can be created!')
            self.conn.commit()

            self.cursor.execute(f'DROP TABLE IF EXISTS {tableFromDict}')

            self.cursor.execute(sqlManager.tablesCreationSQL[tableFromDict])
            with open(f'./chinook/{tableFromDict}.csv', 'r', encoding="utf8") as t:
                dr = csv.DictReader(t)
                to_db = []
                for i in dr:
                    del i["index"]
                    to_db.append(tuple(i.values()))
        except Error as e:
            raise Exception(f"Could not create table {tableFromDict} - ", e)

        self.cursor.executemany(
            f"INSERT OR IGNORE INTO {tableFromDict} VALUES ({','.join(['?'] * len(to_db[0]))});", to_db)
        self.conn.commit()

    def deleteRowFromTable(self, table, value):
        """Deleted the row that applies primary key = {value} from {table}. If there are multiple primary keys, it checks all of them

        Args:
            table (str): table's name
            value (str): the value that primary key should be equal to

        Raises:
            ValueError: When deleting a row, an INTEGER id OR a list with two ids are needed.
            Exception: Could not delete row with primary key = {value} in {table}
        """
        try:
            if type(value) == int:
                self.cursor.execute(
                    f"DELETE FROM {table} WHERE {sqlManager.tablesWhereSQL[table]} = {value}")
            elif len(value) == 2:
                keys = sqlManager.tablesWhereSQL[table].split()
                self.cursor.execute(
                    f"DELETE FROM {table} WHERE {keys[0]} = {value[0]} AND {keys[1]} = {value[1]}")
            else:
                raise ValueError("When deleting a row, an INTEGER id OR a list with two ids are needed.")
            self.conn.commit()
        except Error as e:
            raise Exception(f"Could not delete row with primary key = {value} in table {table} - ", e)
    
    def insertRowToTable(self, table, columns, values):
        """Inserts a new row with {values} in {columns} to {table}

        Args:
            table (str): table's name
            columns (list(str)): columns to add
            values (list(str)): values to add
        Raises:
            ValueError: Primary key must be unique!
            ValueError: Please check cell types (For example you can't insert 'ABC' into an INTEGER type)
        """
        try:
            self.cursor.execute(
                f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join(values)});")
            self.conn.commit()
        except Error as e:
            if e.args[0].startswith('UNIQUE'):
                raise ValueError(f"Primary key must be unique!")
            else:
                raise ValueError(f"Please check cell types (For example you can't insert 'ABC' into an INTEGER type)")

    def checkIfStr(self, table, variable):
        """Checks if {variable} is of type NVARCHAR(X) in {table}

        Args:
            table (str): table's name
            variable (str): variable's name

        Returns:
            Boolean: True if variable is of type NVARCHAR(x), Otherwise False.
        """
        variables = sqlManager.tablesCreationSQL[table]
        if variables[variables.index(f'{variable} '):].startswith(f'{variable} NVARCHAR'):
            return True
        return False

    def updateRow(self, table, condition, value):
        """Updates {value} in all rows that apply {condition} in {table}.

        Args:
            table (str): table's name.
            condition (str): the condition with which we find the wanted rows.
            value (str): the new value that we wish to update.

        Raises:
            ValueError: Can't change primary key.
        """
        try:
            self.cursor.execute(
                f"UPDATE {table} SET {value} WHERE {condition}"
            )
            self.conn.commit()
        except Error as e:
            raise ValueError("Could Not Change Primary Key.")

    def getPreTables(self):
        """Get a list of all the predetermined tables' names.

        Returns:
            list(str): all the predetermined tables' names.
        """
        return sqlManager.tablesCreationSQL.keys()

    def getTables(self):
        """Get a list of all the predetermined that are currently in our DB.

        Returns:
            list(str): all the predetermined that are currently in our DB.
        """
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        return self.cursor.fetchall()

    def getAllFromTable(self, table):
        """Return all rows from {table}.

        Args:
            table (str): table's name.

        Raises:
            ValueError: Could not return all rows from table.

        Returns:
            list: all rows from table.
        """
        try:
            self.cursor.execute(f"SELECT * FROM {table};")
            return self.cursor.fetchall()
        except Error as e:
            raise ValueError(f"Could not select all from table {table} - ", e)

    def getTableColumns(self, table):
        """Return all columns from {table}.

        Args:
            table (str): table's name.

        Raises:
            ValueError: Could not return all columns from table.

        Returns:
            list: all columns from table.
        """
        try:
            if (table,) not in self.getTables():
                return ()
            self.cursor.execute(f'SELECT * FROM {table};')
            description = self.cursor.description
            return [d[0] for d in description]
        except Error as e:
            raise ValueError(f"Could not get table ({table})'s columns - ", e)

    def dropConn(self):
        """Drops the connection to our DB file.
        """
        self.conn.close()


if __name__ == "__main__":
    m = sqlManager('./chinook/chinook.db')
    # m.createDatabaseFromCSV()
    # m.clear()
    # m.dropTable("playlists")
    # m.createTable("playlists")
    # m.deleteRowFromTable('playlists', 1)

    # m.insertRowToTable('playlists', ['1', "'asd'"])
    # m.updateRow('playlists', 'PlaylistId = 1', "Name = 'GOAT'")

    # m.getTableColumns('tracks')

    # m.cursor.execute("SELECT * FROM playlists;")
    # print(m.cursor.fetchall())

    # m.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    # print(m.cursor.fetchall())
    m.dropConn()
