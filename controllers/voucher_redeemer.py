from fastapi import APIRouter

router = APIRouter()

@router.get("/redeem/vouchers")
async def get_vouchers():

    return {"Hello World!":"From Redeemer"}