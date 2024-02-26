from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_database_settings

Base = declarative_base()

# Fetch database settings from config
postgres_config = get_database_settings()

# Create the engine



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

try:
    engine = create_engine(f"postgresql://{postgres_config['username']}:{postgres_config['password']}@{postgres_config['host']}:{postgres_config['port']}/{postgres_config['database']}")
    Base.metadata.create_all(engine)

    # Create a sessionmaker to interact with the database   
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(e)
    quit()
