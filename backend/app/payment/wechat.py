from __future__ import annotations

import hashlib
import uuid
from typing import Any, Dict

import httpx

from app.core.config import settings


class WechatPayService:
    def __init__(self):
        self.app_id = settings.WECHAT_APP_ID
        self.mch_id = settings.WECHAT_MCH_ID
        self.api_key = settings.WECHAT_API_KEY

    def _build_notify_url(self) -> str:
        if not settings.SERVER_PUBLIC_URL:
            raise ValueError("SERVER_PUBLIC_URL is required for payment callbacks")
        base = settings.SERVER_PUBLIC_URL.rstrip("/")
        return f"{base}{settings.API_V1_STR}/payment/callback/wechat"

    def _generate_sign(self, params: dict) -> str:
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params if v])
        sign_str += f"&key={self.api_key}"
        return hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()

    @staticmethod
    def _dict_to_xml(params: dict) -> str:
        xml = "<xml>"
        for key, value in params.items():
            xml += f"<{key}><![CDATA[{value}]]></{key}>"
        xml += "</xml>"
        return xml

    @staticmethod
    def _xml_to_dict(xml_str: str) -> dict:
        from defusedxml import ElementTree as DefusedET

        root = DefusedET.fromstring(xml_str)
        return {child.tag: child.text for child in root}

    async def create_order(
        self,
        order_no: str,
        amount: int,
        description: str,
        client_ip: str = "127.0.0.1",
        trade_type: str = "NATIVE",
    ) -> Dict[str, Any]:
        params = {
            "appid": self.app_id,
            "mch_id": self.mch_id,
            "nonce_str": uuid.uuid4().hex,
            "body": description,
            "out_trade_no": order_no,
            "total_fee": str(amount),
            "spbill_create_ip": client_ip,
            "notify_url": self._build_notify_url(),
            "trade_type": trade_type,
        }
        params["sign"] = self._generate_sign(params)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.mch.weixin.qq.com/pay/unifiedorder",
                content=self._dict_to_xml(params),
                headers={"Content-Type": "application/xml"},
                timeout=30.0,
            )

        result = self._xml_to_dict(response.text)
        if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
            return {
                "success": True,
                "prepay_id": result.get("prepay_id"),
                "code_url": result.get("code_url"),
                "order_no": order_no,
            }

        return {
            "success": False,
            "error": result.get("return_msg") or result.get("err_code_des"),
        }

    async def query_order(self, order_no: str) -> Dict[str, Any]:
        params = {
            "appid": self.app_id,
            "mch_id": self.mch_id,
            "out_trade_no": order_no,
            "nonce_str": uuid.uuid4().hex,
        }
        params["sign"] = self._generate_sign(params)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.mch.weixin.qq.com/pay/orderquery",
                content=self._dict_to_xml(params),
                headers={"Content-Type": "application/xml"},
                timeout=30.0,
            )

        result = self._xml_to_dict(response.text)
        if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
            return {
                "success": True,
                "trade_state": result.get("trade_state"),
                "transaction_id": result.get("transaction_id"),
                "order_no": order_no,
            }

        return {"success": False, "error": result.get("return_msg")}

    def verify_callback(self, xml_data: str) -> Dict[str, Any]:
        result = self._xml_to_dict(xml_data)
        sign = result.pop("sign", None)
        expected_sign = self._generate_sign(result)

        if sign != expected_sign:
            return {"success": False, "error": "Invalid signature"}

        if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
            return {
                "success": True,
                "order_no": result.get("out_trade_no"),
                "transaction_id": result.get("transaction_id"),
                "total_fee": int(result.get("total_fee", 0)),
            }

        return {"success": False, "error": "Payment failed"}


wechat_pay_service = WechatPayService()
