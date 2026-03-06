from __future__ import annotations

import base64
import json
import time
from typing import Any, Dict
from urllib.parse import urlencode

import httpx
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
)

from app.core.config import settings
from app.core.exceptions import InternalServerException
from app.core.logging import logger


class AlipayService:
    def __init__(self):
        self.app_id = settings.ALIPAY_APP_ID
        self.private_key = settings.ALIPAY_PRIVATE_KEY
        self.public_key = settings.ALIPAY_PUBLIC_KEY
        self.gateway = "https://openapi.alipay.com/gateway.do"
        self.return_url = "/payment/result"

    def _build_notify_url(self) -> str:
        if not settings.SERVER_PUBLIC_URL:
            raise InternalServerException("SERVER_PUBLIC_URL is required for payment callbacks")
        base = settings.SERVER_PUBLIC_URL.rstrip("/")
        return f"{base}{settings.API_V1_STR}/payment/callback/alipay"

    @staticmethod
    def _normalize_private_key(key_content: str) -> str:
        if key_content.startswith("-----BEGIN"):
            return key_content
        return (
            "-----BEGIN RSA PRIVATE KEY-----\n"
            f"{key_content}\n"
            "-----END RSA PRIVATE KEY-----"
        )

    @staticmethod
    def _normalize_public_key(key_content: str) -> str:
        if key_content.startswith("-----BEGIN"):
            return key_content
        return (
            "-----BEGIN PUBLIC KEY-----\n"
            f"{key_content}\n"
            "-----END PUBLIC KEY-----"
        )

    @staticmethod
    def _canonical_value(value: Any) -> str:
        if isinstance(value, (dict, list)):
            return json.dumps(value, separators=(",", ":"), ensure_ascii=False)
        return str(value)

    def _build_sign_content(self, params: dict) -> str:
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        return "&".join(
            f"{k}={self._canonical_value(v)}"
            for k, v in sorted_params
            if v is not None and v != "" and k not in {"sign", "sign_type"}
        )

    def _sign(self, params: dict) -> str:
        if not self.private_key:
            raise InternalServerException("Alipay private key is not configured")

        sign_content = self._build_sign_content(params)
        try:
            private_key = load_pem_private_key(
                self._normalize_private_key(self.private_key).encode("utf-8"),
                password=None,
                backend=default_backend(),
            )
            signature = private_key.sign(
                sign_content.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return base64.b64encode(signature).decode("utf-8")
        except Exception as exc:
            logger.error("Alipay signing failed: %s", str(exc))
            raise InternalServerException("Failed to sign Alipay request")

    def _verify_signature(self, params: dict, signature_b64: str) -> bool:
        if not self.public_key:
            logger.error("Alipay public key is not configured")
            return False

        try:
            public_key = load_pem_public_key(
                self._normalize_public_key(self.public_key).encode("utf-8"),
                backend=default_backend(),
            )
            public_key.verify(
                base64.b64decode(signature_b64),
                self._build_sign_content(params).encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except (InvalidSignature, ValueError) as exc:
            logger.warning("Alipay signature verification failed: %s", str(exc))
            return False

    async def create_order(self, order_no: str, amount: float, subject: str) -> Dict[str, Any]:
        biz_content = {
            "out_trade_no": order_no,
            "total_amount": str(amount),
            "subject": subject,
            "product_code": "FAST_INSTANT_TRADE_PAY",
        }
        params = {
            "app_id": self.app_id,
            "method": "alipay.trade.page.pay",
            "format": "JSON",
            "return_url": self.return_url,
            "notify_url": self._build_notify_url(),
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": json.dumps(biz_content, separators=(",", ":"), ensure_ascii=False),
        }
        params["sign"] = self._sign(params)

        return {
            "success": True,
            "pay_url": f"{self.gateway}?{urlencode(params)}",
            "order_no": order_no,
        }

    async def query_order(self, order_no: str) -> Dict[str, Any]:
        biz_content = {"out_trade_no": order_no}
        params = {
            "app_id": self.app_id,
            "method": "alipay.trade.query",
            "format": "JSON",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": json.dumps(biz_content, separators=(",", ":"), ensure_ascii=False),
        }
        params["sign"] = self._sign(params)

        async with httpx.AsyncClient() as client:
            response = await client.post(self.gateway, data=params, timeout=30.0)
            result = response.json()

        if "alipay_trade_query_response" in result:
            query_result = result["alipay_trade_query_response"]
            if query_result.get("code") == "10000":
                return {
                    "success": True,
                    "trade_status": query_result.get("trade_status"),
                    "transaction_id": query_result.get("trade_no"),
                    "order_no": order_no,
                }

        return {"success": False, "error": result.get("msg", "Query failed")}

    def verify_callback(self, params: dict) -> Dict[str, Any]:
        payload = dict(params)
        sign = payload.pop("sign", None)
        payload.pop("sign_type", None)

        if not sign or not self._verify_signature(payload, sign):
            return {"success": False, "error": "Invalid signature"}

        trade_status = payload.get("trade_status")
        if trade_status in {"TRADE_SUCCESS", "TRADE_FINISHED"}:
            return {
                "success": True,
                "order_no": payload.get("out_trade_no"),
                "transaction_id": payload.get("trade_no"),
                "total_amount": float(payload.get("total_amount", 0)),
            }

        return {"success": False, "error": f"Trade status: {trade_status}"}


alipay_service = AlipayService()
