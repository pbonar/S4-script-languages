import sys
import inquirer
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine

from models import Rentals, Stations


def db_connect(db_name: str) -> Session:
    engine = create_engine(f'sqlite:///{db_name}.sqlite3')
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    return session


def get_station_names(session: Session) -> list:
    stations = session.query(Stations).all()
    return [station.name.encode("utf-8") for station in stations]


def avg_rental_time_starting_at_station(session: Session, station_name: str) -> float:
    station = session.query(Stations).filter_by(name=station_name).first()
    
    if station is None:
        print(f"Station '{station_name}' not found.")
        sys.exit(1)
    
    rentals = session.query(Rentals).filter_by(rental_station_id=station.station_id).all()
    
    if len(rentals) == 0:
        print(f"No rentals found for station '{station_name}'.")
        sys.exit(1)
    
    total_time = 0
    for rental in rentals:
        total_time += (rental.end_time - rental.start_time).total_seconds()
    
    return total_time / len(rentals)


def avg_rental_time_ending_at_station(session: Session, station_name: str) -> float:
    station = session.query(Stations).filter_by(name=station_name).first()
    
    if station is None:
        print(f"Station '{station_name}' not found.")
        sys.exit(1)
    
    rentals = session.query(Rentals).filter_by(return_station_id=station.station_id).all()
    
    if len(rentals) == 0:
        print(f"No rentals found for station '{station_name}'.")
        sys.exit(1)
    
    total_time = 0
    for rental in rentals:
        total_time += (rental.end_time - rental.start_time).total_seconds()
    
    return total_time / len(rentals)


def number_of_different_bikes_parked_at_station(session: Session, station_name: str) -> int:
    station = session.query(Stations).filter_by(name=station_name).first()
    
    if station is None:
        print(f"Station '{station_name}' not found.")
        sys.exit(1)
    
    rentals = session.query(Rentals).filter_by(return_station_id=station.station_id).all()
    
    if len(rentals) == 0:
        print(f"No rentals found for station '{station_name}'.")
        sys.exit(1)
    
    bikes = set()
    for rental in rentals:
        bikes.add(rental.bike_number)
    
    return len(bikes)


def bike_number_most_returned_at_station(session: Session, station_name: str) -> int | str:
    station = session.query(Stations).filter_by(name=station_name).first()
    
    if station is None:
        print(f"Station '{station_name}' not found.")
        sys.exit(1)
    
    rentals = session.query(Rentals).filter_by(return_station_id=station.station_id).all()
    
    if len(rentals) == 0:
        return "N/A"
    
    bike_numbers = [rental.bike_number for rental in rentals]
    return max(set(bike_numbers), key=bike_numbers.count)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python load_data.py <database_name>")
        sys.exit(1)

    db_name = sys.argv[1]
    session = db_connect(db_name)
    
    station_names = get_station_names(session)
    station_names = sorted(station_names)
    
    questions = [
        inquirer.List(
            "station",
            message="Select a station:",
            choices=station_names,
            carousel=True
        )
    ]
    answer = inquirer.prompt(questions)
    station_name: str = answer["station"].decode("utf-8")
    
    print(f">> {station_name} <<")
    
    seconds = avg_rental_time_starting_at_station(session, station_name)
    print(f"> Average rental time starting at {station_name}: {int(seconds // 60)} minutes and {(seconds % 60):0.2f} seconds.")
    
    seconds = avg_rental_time_ending_at_station(session, station_name)
    print(f"> Average rental time ending at {station_name}: {int(seconds // 60)} minutes and {(seconds % 60):0.2f} seconds.")
    
    bikes = number_of_different_bikes_parked_at_station(session, station_name)
    print(f"> Number of different bikes parked at {station_name}: {bikes}")

    most_common_bike = bike_number_most_returned_at_station(session, station_name)
    print(f"> Most common bike number at {station_name}: {most_common_bike}")


if __name__ == "__main__":
    main()
    