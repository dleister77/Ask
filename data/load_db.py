import pathlib
import sys
import mysql.connector as mysql

import settings
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
    print(f'Finished loading: {file_name}')


def process_imports(import_arg):
    import_path_str = f'{settings.db_import_path}/{import_arg}'
    import_path = pathlib.Path(import_path_str)
    if import_path.is_file():
        run_load(str(import_path))
    elif import_path.is_dir():
        for file in import_path.iterdir():
            run_load(str(file))


if __name__ == '__main__':
    import_arg = sys.argv[1]
    process_imports(import_arg)
