from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

class Voucher(Base):
    '''
    Define Voucher Table
    '''
    __tablename__ = 'voucher'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False)
    max_redemptions = Column(Integer, nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    is_infinite = Column(Boolean, nullable=False)

class RedemptionDate(Base):
    '''
    Define Redemption Table
    '''
    __tablename__ = 'redemption_dates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    voucher_code = Column(String, ForeignKey('voucher.code'), nullable=False)
    redeemed_at = Column(DateTime, nullable=False)


engine = create_engine("postgresql://dev:devuser@localhost:5432/dev_db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
