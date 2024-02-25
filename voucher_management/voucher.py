from fastapi import HTTPException
from database.database import SessionLocal
from database.database import Voucher, RedemptionDate
import typing

class VoucherRepository:
    @staticmethod
    def store(voucher: Voucher) -> Voucher:
        '''
        Insert a voucher into voucher table
        '''
        session = SessionLocal()
        try:
            session.add(voucher)
            session.commit()
            session.refresh(voucher)
            return voucher
        
        except Exception as e:
                print(f"An error occurred: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        finally:
            session.close()

    @staticmethod
    def get_one(code: str) -> Voucher:
        '''
        Get a voucher from the vpuchers Table
        '''
        with SessionLocal() as session:
            try:
                Voucher.code
                voucher = session.query(Voucher).filter_by(code=code).first()
                return voucher
            
            except Exception as e:
                print(f"An error occurred: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
            
    @staticmethod
    def get_all() -> typing.List[Voucher]:
        '''
        Get list of all vouchers from vouchers table
        '''
       
        with SessionLocal() as session:
            try:
                vouchers = session.query(Voucher).all()
                return vouchers
            except Exception as e:
                print(f"An error occurred: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
            
    @staticmethod
    def update(voucher: Voucher):
        '''
        Update a voucher in vouchers table
        '''
        with SessionLocal() as session:
            try:
                session.merge(voucher)
                session.commit()
            except Exception as e:
                print(f"An error occurred: {e}")
                session.rollback()
                raise HTTPException(status_code=500, detail="Internal server error")
    
    @staticmethod
    def delete(code: str) -> bool:
        '''
        delete a voucher from vouchers table
        '''
        with SessionLocal() as session:
            voucher = session.query(Voucher).filter_by(code=code).first()
            if voucher:
                session.delete(voucher)
                session.commit()
                return True
            return False

class RedemptionDateRepository:
    @staticmethod
    def create(redemption_date: RedemptionDate):
        '''
        Inster redemtion record to RedemtionDate Table
        '''
        session = SessionLocal()
        try:
            session.add(redemption_date)
            session.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            session.rollback()
            raise HTTPException(status_code=500, detail="Internal server error")
        finally:
            session.close()