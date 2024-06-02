import sys
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Rentals, Stations
from create_database import create_database


def get_or_create_station(session: Session, station_name) -> Stations:
    station = session.query(Stations).filter_by(name=station_name).first()
    
    if station is None:
        station = Stations(name=station_name)
        session.add(station)
        session.commit()
    return station


def load_data(csv_file: str, db_name: str) -> None:
    create_database(db_name)
    engine = create_engine(f'sqlite:///{db_name}.sqlite3')

    Session = sessionmaker(bind=engine)
    session = Session()

    data = pd.read_csv(csv_file, encoding='utf-8')

    for index, row in data.iterrows():
        percentage = (index + 1) / len(data) * 100
        print(f"Progress: {index + 1}/{len(data)} ({percentage:.2f} %)", end='\r')
        
        rental_station = get_or_create_station(session, row['Stacja wynajmu'])
        return_station = get_or_create_station(session, row['Stacja zwrotu'])

        rental = Rentals(
            bike_number=row['Numer roweru'],
            start_time=pd.to_datetime(row['Data wynajmu']),
            end_time=pd.to_datetime(row['Data zwrotu']),
            rental_station_id=rental_station.station_id,
            return_station_id=return_station.station_id
        )
        session.add(rental)

    session.commit()
    print(f"Data from '{csv_file}' has been loaded successfully into '{db_name}.sqlite3'.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python load_data.py <csv_file> <database_name>")
        sys.exit(1)

    csv_file = sys.argv[1]
    db_name = sys.argv[2]
    load_data(csv_file, db_name)
