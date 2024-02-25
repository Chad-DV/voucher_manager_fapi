from pydantic import BaseModel, validator
from datetime import datetime, timedelta
import uuid

def generate_unique_code() -> str:
    '''
    Generate a unique ID for vouchers
    '''
    unique_id = uuid.uuid4().hex
    return unique_id[:10]

class DefaultVoucher(BaseModel):
    '''
    Default voucher config
    '''
    code: str = generate_unique_code()
    max_redemptions: int = 1
    valid_from: datetime = datetime.now()
    valid_to:   datetime = datetime.now() + timedelta(days=2)
    is_infinite:bool = False

    #function ensures max_redemptions var is positive 
    @validator("max_redemptions")
    def check_max_redemptions(cls, v):
        '''
        Check if max redemtions is positive
        '''
        if v <= 0:
            raise ValueError("max_redemptions must be positive")
        return v
