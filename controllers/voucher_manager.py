import datetime
from typing import List,Dict
from fastapi import APIRouter, HTTPException
from models import VoucherPayload
from my_redis import redis_client
import random 
import string

router = APIRouter()

#---Routes---#

@router.post("/vouchers/{max_redemptions}/{expiry_date}")
async def create_voucher(max_redemptions: int, expiry_date: datetime.datetime) -> VoucherPayload:
    if max_redemptions < 0:
        raise HTTPException(status_code=400, detail="max_redemptions must be positive")
    elif max_redemptions == 0:
        raise HTTPException(status_code=400, detail="Voucher has been redeemed")
    try:
        voucher_code = generate_unique_code()
    except RuntimeError:
        raise HTTPException(status_code=500, detail="Failed to generate a unique voucher code")

    voucher_id = redis_client.incr("voucher_ids")

    # Store voucher details in Redis
    voucher_data = {
        "id": voucher_id,
        "code": voucher_code,
        "max_redemptions": max_redemptions,
        "expiry_date": expiry_date.isoformat() if expiry_date else None
    }
    redis_client.hmset(f"voucher:{voucher_id}", voucher_data) # type: ignore redis will change it to bytes

    return VoucherPayload(**voucher_data)

@router.post("/vouchers/{max_redemptions}", response_model=VoucherPayload)
async def create_voucher_with_default_expiry(max_redemptions: int):

    if max_redemptions <= 0:
        raise HTTPException(status_code=400, detail="max_redemptions must be positive")

    # Calculate expiry date as 24 hours from now
    expiry_date = datetime.datetime.utcnow() + datetime.timedelta(hours=24)

    voucher_id = redis_client.incr("voucher_ids")
    voucher_code = generate_unique_code()
    voucher_data = {
        "id": voucher_id,
        "code": voucher_code,
        "max_redemptions": max_redemptions,
        "expiry_date": expiry_date.strftime("%Y-%m-%dT%H:%M:%S")
    }
    redis_client.hmset(f"voucher:{voucher_id}", voucher_data)  # type: ignore redis will change it to bytes

    return VoucherPayload(**voucher_data)
    
@router.get("/vouchers/{voucher_id}")
async def get_voucher_by_id(voucher_id: int) -> VoucherPayload:
    # get voucher matching passed ID
    voucher_data = redis_client.hgetall(f"voucher:{voucher_id}")

    if not voucher_data:
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    return bytes_dict_to_voucher_payload(voucher_data)
    
@router.get("/vouchers")
async def get_all_vouchers() -> List[VoucherPayload]:
    
    voucher_keys = redis_client.keys("voucher:*")
    vouchers = []

    for voucher_key in voucher_keys:
        voucher_data = redis_client.hgetall(voucher_key)
        if voucher_data:
            vouchers.append(bytes_dict_to_voucher_payload(voucher_data))
    
    if not vouchers:
        raise HTTPException(status_code=404, detail="No vouchers found")

    return vouchers


@router.put("/vouchers/{voucher_id}/{new_max_redemptions}/{new_expiry_date}")
async def update_voucher_by_id(
    voucher_id: int,
    new_max_redemptions: int,
    new_expiry_date: str
):
    if new_max_redemptions <= 0:
        raise HTTPException(status_code=400, detail="Max redemptions must be a positive integer")

    if not redis_client.exists(f"voucher:{voucher_id}"):
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    current_voucher_data = redis_client.hgetall(f"voucher:{voucher_id}")
    current_voucher_data = {key.decode("utf-8"): value.decode("utf-8") for key, value in current_voucher_data.items()}
    current_voucher_data['max_redemptions'] = new_max_redemptions # type: ignore
    current_voucher_data['expiry_date'] = new_expiry_date

    redis_client.hmset(f"voucher:{voucher_id}", current_voucher_data) # type: ignore

    # Return the updated voucher
    return {"message": "Voucher updated successfully", "voucher": current_voucher_data}
    
@router.delete("/vouchers/{voucher_id}")
async def delete_voucher_by_id(voucher_id: int):

    if not redis_client.exists(f"voucher:{voucher_id}"):
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    redis_client.delete(f"voucher:{voucher_id}")

    return {"message": "Voucher deleted successfully"}

#---Helper_Functions---#
def generate_unique_code():
    '''Generate a unique voucher code. if 10 attempts fail to generate the code the request fails'''

    max_attempts = 10
    for _ in range(max_attempts):
        # Generate a random code
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        if not redis_client.sismember("code", code):
            return code
    raise RuntimeError("Failed to generate a unique voucher code after maximum attempts")

def bytes_dict_to_voucher_payload(data: Dict[bytes, bytes]) -> VoucherPayload:
    '''Convierts byte dict to VoucherPayload model '''
    voucher_data = {
        "id": int(data[b'id']),
        "code": data[b'code'].decode(),
        "max_redemptions": int(data[b'max_redemptions']),
        "expiry_date": datetime.datetime.fromisoformat(data[b'expiry_date'].decode()) if data[b'expiry_date'] else None
    }
    
    return VoucherPayload(**voucher_data)

