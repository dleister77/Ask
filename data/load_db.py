import sys
import mysql.connector as mysql

from db import get_db, load_provider_file


def run_load(file_name):
    with get_db() as db:
        try:
            cursor = db.cursor(named_tuple=True)
            load_provider_file(file_name, cursor, db)
            db.commit()
        except mysql.Error as e:
            print(f"Failed to load due to error: {e}")
            db.rollback()
    print("Finished loading")



if __name__ == '__main__':
    import_file = sys.argv[1]
    import_file = f'/home/leisterbrau/projects/scraping/output/{import_file}'
    run_load(import_file)

        
