import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, DateTime

class Base(DeclarativeBase):
    pass

class Stations(Base):
    __tablename__ = "stations"

    station_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column()

class Rentals(Base):
    __tablename__ = "rentals"

    rental_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bike_number: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    rental_station_id: Mapped[int] = mapped_column(Integer, ForeignKey('stations.station_id'))
    return_station_id: Mapped[int] = mapped_column(Integer, ForeignKey('stations.station_id'))

    rental_station = relationship("Stations", foreign_keys=[rental_station_id], backref="rentals_start")
    return_station = relationship("Stations", foreign_keys=[return_station_id], backref="rentals_end")
