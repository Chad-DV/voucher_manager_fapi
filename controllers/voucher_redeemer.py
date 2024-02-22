from datetime import datetime
from typing import List,Dict
from fastapi import APIRouter, HTTPException
from models import VoucherPayload
from my_redis import redis_client
router = APIRouter()

@router.post("/redeem/vouchers/{voucher_code}")
async def redeem_voucher_by_code(voucher_code: str):

    voucher_keys = redis_client.keys("voucher:*")
    for voucher_key in voucher_keys:
        voucher_data = redis_client.hgetall(voucher_key)
        if voucher_data.get(b"code") == voucher_code.encode('utf-8'):
            
            if redis_client.sismember("redeemed_vouchers", voucher_key):
                raise HTTPException(status_code=400, detail="Voucher already redeemed")

            # Check if the voucher is still valid
            expiry_date_str = voucher_data.get(b"expiry_date")
            if expiry_date_str:
                expiry_date = datetime.fromisoformat(expiry_date_str.decode('utf-8')) # type: ignore
                if expiry_date < datetime.utcnow():
                    raise HTTPException(status_code=400, detail="Voucher has expired")

            # Check fro max redemptions
            max_redemptions = int(voucher_data.get(b"max_redemptions", 0))
            if max_redemptions <= 0:
                raise HTTPException(status_code=400, detail="Maximum redemptions must be larger than 0")


            redis_client.sadd("redeemed_vouchers", voucher_key)
            redis_client.hset(voucher_key, "max_redemptions", max_redemptions - 1)

            return {"message": "Voucher redeemed successfully"}

    # If voucher not found, raise 404 error
    raise HTTPException(status_code=404, detail="Voucher not found")


@router.get("/redeem/vouchers", response_model=List[VoucherPayload])
async def get_redeemed_vouchers():

    redeemed_voucher_keys = redis_client.smembers("redeemed_vouchers")
    if not redeemed_voucher_keys:
        return {"message": "No redeemed vouchers found"}

    # Retrieve voucher data for each redeemed voucher key
    redeemed_vouchers = []
    for voucher_key in redeemed_voucher_keys:
        voucher_data = redis_client.hgetall(voucher_key)
        max_redemptions = int(voucher_data.get(b"max_redemptions", 0))
        if max_redemptions == 0:
            redeemed_vouchers.append(bytes_dict_to_voucher_payload(voucher_data))

    return redeemed_vouchers

@router.get("/redeem/vouchers/expiring")
async def get_vouchers_before_expiry():
   

    current_time = datetime.utcnow()

    voucher_keys = redis_client.keys("voucher:*")
    valid_vouchers = []

    for voucher_key in voucher_keys:
        voucher_data = redis_client.hgetall(voucher_key)
        expiry_date_str = voucher_data.get(b"expiry_date")
        if expiry_date_str:
            expiry_date = datetime.fromisoformat(expiry_date_str) # type: ignore
            if expiry_date > current_time:
                valid_vouchers.append(bytes_dict_to_voucher_payload(voucher_data)) 

    return valid_vouchers


def bytes_dict_to_voucher_payload(data: Dict[bytes, bytes]) -> VoucherPayload:

    voucher_data = {
        "id": int(data[b'id']),
        "code": data[b'code'].decode(),
        "max_redemptions": int(data[b'max_redemptions']),
        "expiry_date": datetime.fromisoformat(data[b'expiry_date'].decode()) if data[b'expiry_date'] else None
    }
    
    return VoucherPayload(**voucher_data)