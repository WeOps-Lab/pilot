import asyncio
import base64
import inspect
import os
from logging import getLogger
from typing import Dict, Optional, Text, Any, Callable, Awaitable

import xmltodict
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from wechatpy import WeChatClient, parse_message
from wechatpy.utils import check_signature, to_text

from eventbus.notification_eventbus import NotificationEventBus

logger = getLogger(__name__)


class WechatOfficialAccountChannel(InputChannel):
    def name(self) -> Text:
        return "wechat_official_account"

    def __init__(self, appid, secret, token, aes_key, enable_eventbus) -> None:
        super().__init__()

        self.appid = appid
        self.secret = secret
        self.token = token
        self.aes_key = base64.b64decode(aes_key + "=")
        logger.info(f"WechatOfficialAccountChannel init called，app_id={appid}, secret={secret}, token={token}, aes_key={aes_key}")
        # self.crypto = WeChatCrypto(token, aes_key, appid)

        self.wechat_client = WeChatClient(
            appid,
            secret
        )

        self.bot_id = os.getenv('MUNCHKIN_BOT_ID', "")
        if enable_eventbus:
            queue_name = f"wechat_official_account_{self.bot_id}"
            logger.info(f"启动Pilot消息总线:[{queue_name}]")
            self.event_bus = NotificationEventBus()
            self.event_bus.consume(queue_name, self.process_event)

    def process_event(self, event):
        # 接收到不属于通知类型的消息
        if self.event_bus.is_notification_event(event) is False:
            return

        # 接受到不属于本通道的消息
        if event['integration'] != "" and event['integration'] != "enterprise_wechat":
            return

        reply_user_id = self.event_bus.get_notification_event_sender_id(event)
        reply_text = self.event_bus.get_notification_event_content(event)

        logger.info(f"收到消息总线通知,目标用户:[{reply_user_id}],内容:[{reply_text}]")

        reply_text = reply_text.strip()
        reply_text_list = reply_text.split("\n")

        # 30行一个batch进行发送
        for i in range(0, len(reply_text_list), 50):
            msg = "\n".join(reply_text_list[i:i + 50])
            self.wechat_client.message.send_markdown(reply_user_id, msg)

        logger.debug(f'投递消息成功,目标用户[{reply_user_id}]')

    def decrypt(self, msg_encrypt):
        try:
            cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])
            ciphertext_decoded = base64.b64decode(msg_encrypt)
            plaintext_padded = cipher.decrypt(ciphertext_decoded)
            plaintext = unpad(plaintext_padded, AES.block_size)
            xml_len = int.from_bytes(plaintext[16:20], byteorder='big')
            xml_content = plaintext[20:20 + xml_len].decode('utf-8')
            return xml_content
        except Exception as e:
            return None

    @classmethod
    def from_credentials(cls, credentials: Optional[Dict[Text, Any]]) -> "InputChannel":
        return cls(
            credentials.get("appid"),
            credentials.get("secret"),
            str(credentials.get("token")),
            credentials.get("aes_key"),
            credentials.get("enable_eventbus", False),
        )

    async def send_message(self, on_new_message, query, reply_user_id):
        try:
            if not query:
                return
            logger.info(f"[Received message]:{query}")

            context = dict()
            context['from_user_id'] = reply_user_id
            collector = CollectingOutputChannel()

            await on_new_message(
                UserMessage(
                    text=query,
                    output_channel=collector,
                    sender_id=reply_user_id,
                    input_channel=self.name(),
                    metadata=None,
                )
            )

            response_data = collector.messages
            reply_text = (
                "\n\n".join(data["text"] for data in response_data)
                .replace("bot:", "")
                .strip()
            )
            reply_text_list = reply_text.split("\n")
            for i in range(0, len(reply_text_list), 50):
                msg = "\n".join(reply_text_list[i:i + 50])
                self.wechat_client.message.send_text(reply_user_id, msg)
        except Exception as error:
            logger.error(error)

    def blueprint(
            self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:
        wechat_official_account_hook = Blueprint(
            f"wechat_official_account_hook_{type(self).__name__}",
            inspect.getmodule(self).__name__,
        )

        @wechat_official_account_hook.route("/", methods=["GET"])
        async def index(request: Request) -> HTTPResponse:
            signature = request.args.get('signature')
            timestamp = request.args.get('timestamp')
            nonce = request.args.get('nonce')
            echostr = request.args.get('echostr')

            logger.info(
                f'WeChat verification: msg_signature:{signature}, timestamp:{timestamp}, nonce:{nonce}, echostr:{echostr}')

            check_signature(self.token, signature, timestamp, nonce)
            return response.text(echostr)

        @wechat_official_account_hook.route("/", methods=["POST"])
        async def msg_entry(request: Request) -> HTTPResponse:
            xml_msg = xmltodict.parse(to_text(request.body))['xml']
            decode_msg = self.decrypt(xml_msg['Encrypt'])
            message = parse_message(decode_msg)
            if message.type == "text":
                asyncio.create_task(self.send_message(
                    on_new_message,
                    message.content,
                    message.source,
                ))
            return HTTPResponse(body="")
        return wechat_official_account_hook
