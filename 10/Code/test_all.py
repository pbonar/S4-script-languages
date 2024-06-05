import os
from load_data import load_data
from get_stats_for_station import db_connect, avg_rental_time_starting_at_station, avg_rental_time_ending_at_station, number_of_different_bikes_parked_at_station, bike_number_more_common_at_station


def test_load_data():
    filename = "Data/test_data.csv"
    db_name = "test_db"

    # if the database already exists, delete it
    if os.path.exists(f"{db_name}.sqlite3"):
        os.remove(f"{db_name}.sqlite3")

    load_data(csv_file=filename, db_name=db_name)

    # check if the database was created
    assert os.path.exists(f"{db_name}.sqlite3")

    # connect to the db
    from sqlite3 import connect
    connection = connect(f"{db_name}.sqlite3")
    cursor = connection.cursor()

    # check if the tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    assert ("rentals",) in tables
    assert ("stations",) in tables

    # check if the data was loaded
    cursor.execute("SELECT COUNT(*) FROM rentals;")
    assert cursor.fetchone()[0] == 4

    cursor.execute("SELECT COUNT(*) FROM stations;")
    assert cursor.fetchone()[0] == 4


def test_stats():
    db_name = "test_db"

    if not os.path.exists(f"{db_name}.sqlite3"):
        test_load_data()

    # connect
    session = db_connect(db_name)

    # test avg_rental_time_starting_at_station
    assert avg_rental_time_starting_at_station(session, "S2") == 1005616.0

    # test avg_rental_time_ending_at_station
    assert avg_rental_time_ending_at_station(session, "S1") == 1005616.0

    # test number_of_different_bikes_parked_at_station
    assert number_of_different_bikes_parked_at_station(session, "S1") == 1

    # test bike_number_more_common_at_station
    assert bike_number_more_common_at_station(session, "S1") == 1

    # close the session
    session.close()
