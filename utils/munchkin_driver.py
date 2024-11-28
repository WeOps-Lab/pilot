import json

import requests

from core.server_settings import server_settings
from loguru import logger


class MunchkinDriver:
    def execute_single_target_skill(self, skill_id, params, sender_id=''):
        result = self.automation_skills_execute(skill_id, params, sender_id)
        keys = result['return'][0].keys()
        first_key = list(keys)[0]
        return result['return'][0][first_key]

    def automation_skills_execute(self, skill_id, params, sender_id=''):
        result = requests.post(server_settings.munchkin_base_url + '/api/bot/automation_skill_execute', data=json.dumps(
            {
                "bot_id": server_settings.munchkin_bot_id,
                "skill_id": skill_id,
                "params": params,
                "sender_id": sender_id
            }
        ), headers={
            "Authorization": f"TOKEN {server_settings.munchkin_api_key}",
            "Content-Type": "application/json"
        }).json()
        return result

    def chat(self, action_name, user_message, chat_history, sender_id='', enable_online_search=False, channel='socketio'):
        chat_history = chat_history[:server_settings.chatgpt_model_max_history]
        logger.info(
            f"执行[{action_name}]动作,通道:[{channel}],发送者ID:[{sender_id}],消息: {user_message}"
        )

        result = requests.post(server_settings.munchkin_base_url + '/bot_mgmt/skill_execute/', data=json.dumps(
            {
                "bot_id": server_settings.munchkin_bot_id,
                "skill_id": action_name,
                "sender_id": sender_id,
                "user_message": user_message,
                "chat_history": chat_history,
                "enable_online_search": enable_online_search,
                "channel": channel
            }
        ), headers={
            "Authorization": f"TOKEN {server_settings.munchkin_api_key}",
            "Content-Type": "application/json"
        }).json()
        logger.info(f"回答结果： {result}")
        return result['result']
