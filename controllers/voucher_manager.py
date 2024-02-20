import datetime
from fastapi import APIRouter, HTTPException
import redis
from models import VoucherPayload

router = APIRouter()
redis_client = redis.StrictRedis(host='0.0.0.0', port=6379, db=0, decode_responses=True)

@router.get("/manage/vouchers")
async def get_vouchers() -> dict[str, str]:
 
    return {"Hello World!":"From Manager"}

@router.post("/manage/vouchers/{max_redemptions}/{expiry_date}")
async def create_voucher(max_redemptions: int, expiry_date: datetime.datetime) -> VoucherPayload:
    if max_redemptions <= 0:
        raise HTTPException(status_code=400, detail="max_redemptions must be positive")

    # increment ID
    voucher_id = redis_client.incr("voucher_ids")

    # store voucher details in redis
    voucher_data = {
        "id": voucher_id,
        "max_redemptions": max_redemptions,
        "expiry_date": expiry_date.isoformat() if expiry_date else None
    }
    redis_client.hmset(f"voucher:{voucher_id}", voucher_data) # type: ignore

    return VoucherPayload(**voucher_data)
    
    
@router.get("/manage/vouchers/{voucher_id}")
async def get_voucher_by_id(voucher_id: int) -> VoucherPayload:
    # get all form redis vouchers
    voucher_data = redis_client.hgetall(f"voucher:{voucher_id}")

    if not voucher_data:
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    return VoucherPayload(**voucher_data) # type: ignore
    