import sqlite3
from flask import g
from docx import Document


class DBConnection:
    def __init__(self, DB):
        self.DB = DB


    def get_db(self):
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(self.DB)
        return db
    
    
    def execute_query(self, query, params=None):
        conn = self.get_db()
        cursor = conn.cursor()
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        conn.commit()
        return cursor
    
    
    def fetch_all(self, cursor):
        return cursor.fetchall()


    def insert_into_working(self, title, file_path):
        try:
            query = "INSERT INTO working (title, File_Path) VALUES (?, ?)"
            self.execute_query(query, (title, file_path))
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False


    def close_connection(self):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()


    def validate_login(self, email, password):
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        result = cursor.fetchone()
        if result:
            stored_password = result[4]
            if password == stored_password:
                return True, True
            else:
                return True, False
        else:
            return False, False


    def email_exists(self, email):
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE email=?", (email,))
        return cursor.fetchone()[0] > 0
    

    def create_account(self, lname, fname, email, password):
        if self.email_exists(email):
            return False, 'Email already exists.'
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (lname, fname, email, password) VALUES (?, ?, ?, ?)",
                            (lname, fname, email, password))
        conn.commit()
        return True, 'Account created successfully.'
    
    
    def insert_upload(self, title, authors, publicationDate, thesisAdvisor, department, degree, subjectArea, abstract, file_path):
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO uploads (title, authors, publicationDate, thesisAdvisor, department, degree, subjectArea, abstract, file_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                        (title, authors, publicationDate, thesisAdvisor, department, degree, subjectArea, abstract, file_path))
            conn.commit()
            return True
        except Exception as e:
            print("Error inserting record:", e)
            conn.rollback()
            return False
        
    def get_departments(self):
        """Get all departments from the fields table."""
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT Department FROM fields")
            departments = [row[0] for row in cursor.fetchall()]
            return departments
        except Exception as e:
            print("Error getting departments:", e)
            return []
        
    def get_degrees(self, department):
        """Get the degrees for a specific department."""
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT Degree FROM fields WHERE Department = ?", (department,))
            degrees = [row[0] for row in cursor.fetchall()]
            return degrees
        except Exception as e:
            print("Error getting degrees:", e)
            return []

    def get_subject_areas(self, department, degree):
        """Get the subject areas for a specific degree."""
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT "Subject Area" FROM fields WHERE Department = ? AND Degree = ?', (department, degree))
            subject_areas = [row[0] for row in cursor.fetchall()]
            return subject_areas
        except Exception as e:
            print("Error getting subject areas:", e)
            return []
        



        
    def fetch_publications(self, selected_sort, selected_field, selected_year, search_query):
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            query = "SELECT id, title, authors, publicationDate, subjectArea FROM uploads WHERE 1=1"
            params = ()
            if selected_field:
                query += " AND subjectArea = ?"
                params += (selected_field,)
            cursor.execute(query, params)
            items = [{'id': row[0], 'title': row[1], 'authors': row[2], 'year': row[3], 'subjectArea': row[4]} for row in cursor.fetchall()]
            cursor.execute("SELECT DISTINCT subjectArea FROM uploads")
            unique_subject_areas = [row[0] for row in cursor.fetchall()]
            cursor.execute("SELECT DISTINCT substr(publicationDate, 1, 4) FROM uploads")
            unique_years = [row[0] for row in cursor.fetchall()]
            if selected_year:
                items = [item for item in items if item['year'] == selected_year]
            if selected_sort == 'latest':
                items.sort(key=lambda x: x['year'], reverse=True)
            elif selected_sort == 'oldest':
                items.sort(key=lambda x: x['year'])
            else:
                items.sort(key=lambda x: x['title'])
            if search_query:
                search_query = search_query.lower()
                items = [item for item in items if search_query in item['title'].lower() or search_query in item['authors'].lower()]
            return items, unique_subject_areas, unique_years
        except Exception as e:
            print("Error fetching publications:", e)
            return [], [], []


    def fetch_research_publications(self, search_query):
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            query = "SELECT id, title FROM working"
            cursor.execute(query)
            items = [{'id': row[0], 'title': row[1]} for row in cursor.fetchall()]
            if search_query:
                search_query = search_query.lower()
                items = [item for item in items if search_query in item['title'].lower()]
            return items
        except Exception as e:
            print("Error fetching publications:", e)
            return []
        
    def fetch_item_by_id(self, item_id):
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            query = "SELECT id, title, IMRAD FROM working WHERE id = ?"
            cursor.execute(query, (item_id,))
            row = cursor.fetchone()

            if row:
                item = {'id': row[0], 'title': row[1], 'IMRAD': row[2]}
                content = self.read_docx_content(item['IMRAD'])
                item['content'] = content
                return item
            else:
                return None

        except Exception as e:
            print("Error fetching item by ID:", e)
            return None

    def read_docx_content(self, IMRAD):
        doc = Document(IMRAD)
        content = []
        for paragraph in doc.paragraphs:
            content.append(paragraph.text)
        return '\n'.join(content)



        
    def get_publication_by_id(self, item_id):
        try:
            conn = self.get_db()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM uploads WHERE id=?", (item_id,))
            row = cursor.fetchone()

            if row:
                item = {
                    'id': row[0],
                    'title': row[1],
                    'authors': row[2],
                    'year': row[3],
                    'thesisAdvisor': row[4],
                    'department': row[5],
                    'degree': row[6],
                    'subjectArea': row[7],
                    'abstract': row[8],
                    'file_path': row[9]
                }
                return item
            else:
                return None
        except Exception as e:
            print("Error fetching publication:", e)
            return None
        
    def update_converted_file_path(self, item_id, converted_file_path):
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE uploads SET converted_file_path=? WHERE id=?", (converted_file_path, item_id))
            conn.commit()
            return True
        except Exception as e:
            print("Error updating converted file path:", e)
            conn.rollback()
            return False


    def get_last_unapproved(self):
        try:
            conn = self.get_db()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM working ORDER BY id DESC LIMIT 1")
            record = cursor.fetchone()
            return dict(record) if record else None
        except Exception as e:
            print("Error retrieving record:", e)
            return None
        
    def get_heyss_record(self, title):
        try:
            conn = self.get_db()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM heyss WHERE title = ?", (title,))
            record = cursor.fetchone()
            return dict(record) if record else None
        except Exception as e:
            print("Error retrieving record from heyss:", e)
            return None
        
    def get_similar_titles(self, title):
        try:
            conn = self.get_db()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM heysss WHERE title = ?", (title,))
            record = cursor.fetchone()
            return dict(record) if record else None
        except Exception as e:
            print("Error retrieving record:", e)
            return None
    
    
    def get_similar_title(self, title):
        try:
            conn = self.get_db()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM heys WHERE title = ?", (title,))
            record = cursor.fetchone()
            return dict(record) if record else None
        except Exception as e:
            print("Error retrieving record:", e)
            return None



    def update_imrad_path(self, original_file_path, imrad_file_path):
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE working SET IMRAD = ? WHERE file_path = ?", (imrad_file_path, original_file_path))
            conn.commit()
        except Exception as e:
            print("Error updating record:", e)


    def update_abstract(self, id, abstract):
        try:
            conn = self.get_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE working SET abstract = ? WHERE id = ?", (abstract, id))
            conn.commit()
            return True
        except Exception as e:
            print("Error updating record:", e)
            return False

    def get_record_by_title(self, title):
        # Connect to the database
        conn = sqlite3.connect('database.db')
        
        # Create a cursor object
        cur = conn.cursor()
        
        # Execute the SQL query
        cur.execute("SELECT * FROM heys WHERE title = ?", (title,))
        
        # Fetch the first record
        record = cur.fetchone()
        
        # Close the connection
        conn.close()
        
        # If a record was found, convert it to a dictionary
        if record:
            record_dict = {'title': record[0], 'path': record[1]}
            return record_dict
        
        # If no record was found, return None
        return None