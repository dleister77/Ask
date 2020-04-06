from contextlib import contextmanager
import mysql.connector as mysql
import settings


@contextmanager
def get_db():
    try:
        db = mysql.connect(
            host="localhost",
            user=settings.db_user,
            passwd=settings.db_password,
            database=settings.db_name,
            allow_local_infile=True
        )
        yield db
        db.close()
    finally:
        pass


def load_provider_file(filename, cursor, db):
    create_temp = """CREATE TEMPORARY TABLE tmp (
        id int(11) AUTO_INCREMENT PRIMARY KEY,
        name varchar(64),
        category_id int(11),
        telephone varchar(24) NOT NULL,
        website varchar(64) DEFAULT NULL,
        line1 varchar(64) DEFAULT NULL,
        line2 varchar (64) DEFAULT NULL,
        city varchar(64),
        state_id int(11),
        zip varchar(20) DEFAULT NULL,
        latitude float DEFAULT NULL,
        longitude float DEFAULT NULL,
        low_accuracy tinyint(1) DEFAULT 0,
        provider_id int(11) DEFAULT NULL
        );"""
    cursor.execute(create_temp)
    set_autocommit = "SET autocommit = 0;"
    cursor.execute(set_autocommit)
    load_temp = """LOAD DATA LOCAL INFILE %s INTO TABLE tmp FIELDS 
                    TERMINATED BY ','
                    (name, category_id, telephone, website, line1, line2, city,
                    state_id, zip, latitude, longitude, @low_acc_var)
                    SET low_accuracy = @low_acc_var = 'True';"""
    cursor.execute(load_temp, (filename, ))
    copy_provider = """INSERT IGNORE INTO provider
                    (_name, _telephone, website) SELECT name, telephone, website
                    FROM tmp;"""
    cursor.execute(copy_provider)
    update_tmp = """UPDATE tmp JOIN provider ON tmp.telephone=provider._telephone
                    SET tmp.provider_id=provider.id;"""
    cursor.execute(update_tmp)
    copy_address = """INSERT IGNORE INTO address 
                        (_line1, _line2, zip, _city, state_id, provider_id,
                        latitude, longitude, low_accuracy)
                        SELECT line1, line2, zip, city, state_id, provider_id,
                        latitude, longitude, low_accuracy FROM tmp;"""
    cursor.execute(copy_address)
    copy_category = """INSERT IGNORE INTO category_provider
                       (category_id, provider_id) 
                       SELECT category_id, provider_id FROM tmp;"""
    cursor.execute(copy_category)

    cleanup = """DROP TABLE tmp"""
    cursor.execute(cleanup)   





