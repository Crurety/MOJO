from __future__ import annotations

import hashlib
import time
from typing import Any, Dict

import httpx

from app.core.config import settings


class UnionPayService:
    def __init__(self):
        self.merchant_id = settings.UNIONPAY_MERCHANT_ID
        self.api_key = settings.UNIONPAY_API_KEY
        self.gateway = "https://gateway.95516.com"

    def _build_notify_url(self) -> str:
        if not settings.SERVER_PUBLIC_URL:
            raise ValueError("SERVER_PUBLIC_URL is required for payment callbacks")
        base = settings.SERVER_PUBLIC_URL.rstrip("/")
        return f"{base}{settings.API_V1_STR}/payment/callback/unionpay"

    def _build_front_url(self) -> str:
        if not settings.SERVER_PUBLIC_URL:
            raise ValueError("SERVER_PUBLIC_URL is required for payment callbacks")
        base = settings.SERVER_PUBLIC_URL.rstrip("/")
        return f"{base}/payment/result"

    def _generate_sign(self, params: dict) -> str:
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params if v])
        return hashlib.sha256((sign_str + str(self.api_key)).encode("utf-8")).hexdigest().upper()

    async def create_order(self, order_no: str, amount: int, subject: str) -> Dict[str, Any]:
        params = {
            "merId": self.merchant_id,
            "orderId": order_no,
            "txnAmt": str(amount),
            "txnTime": time.strftime("%Y%m%d%H%M%S"),
            "orderDesc": subject,
            "notifyUrl": self._build_notify_url(),
            "frontUrl": self._build_front_url(),
            "txnType": "01",
            "txnSubType": "01",
            "bizType": "000201",
            "channelType": "07",
            "accessType": "0",
            "currencyCode": "156",
        }
        params["signature"] = self._generate_sign(params)

        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return {
            "success": True,
            "pay_url": f"{self.gateway}/gateway/api/frontTransReq.do?{query}",
            "order_no": order_no,
        }

    async def query_order(self, order_no: str) -> Dict[str, Any]:
        params = {
            "merId": self.merchant_id,
            "orderId": order_no,
            "txnTime": time.strftime("%Y%m%d%H%M%S"),
            "txnType": "00",
            "txnSubType": "00",
            "bizType": "000000",
            "accessType": "0",
        }
        params["signature"] = self._generate_sign(params)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.gateway}/gateway/api/queryTrans.do",
                data=params,
                timeout=30.0,
            )

        result = response.json()
        if result.get("respCode") == "00":
            return {
                "success": True,
                "trade_status": result.get("origRespCode"),
                "transaction_id": result.get("queryId"),
                "order_no": order_no,
            }

        return {"success": False, "error": result.get("respMsg", "Query failed")}

    def verify_callback(self, params: dict) -> Dict[str, Any]:
        payload = dict(params)
        signature = payload.pop("signature", None)
        expected_sign = self._generate_sign(payload)

        if signature != expected_sign:
            return {"success": False, "error": "Invalid signature"}

        if payload.get("respCode") == "00":
            return {
                "success": True,
                "order_no": payload.get("orderId"),
                "transaction_id": payload.get("queryId"),
                "total_amount": int(payload.get("txnAmt", 0)),
            }

        return {"success": False, "error": f"Response code: {payload.get('respCode')}"}


unionpay_service = UnionPayService()
