import requests
import logging

class ZentaoHandler:
    def __init__(self, base_url, account, password):
        self.base_url = base_url.rstrip('/')
        self.account = account
        self.password = password
        self.token = self.get_token()
        self.headers = {"Token": self.token}

    def get_token(self):
        """向禅道请求新的 token"""
        try:
            url = f"{self.base_url}/tokens"
            payload = {"account": self.account, "password": self.password}
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            token = response.json().get("token")
            if token:
                logging.info("Successfully retrieved Zentao token.")
                return token
            else:
                logging.error("No token returned from Zentao.")
        except Exception as e:
            logging.exception(f"Failed to get token from Zentao: {e}")
        return None

    def refresh_token(self):
        self.token = self.get_token()
        self.headers = {"Token": self.token}

    def request_with_auto_refresh(self, method, url, **kwargs):
        """通用请求方法，自动刷新过期 token 并重试一次"""
        response = requests.request(method, url, headers=self.headers, **kwargs)
        if response.status_code == 401:  # Token 过期或无效
            logging.warning("Zentao token expired. Refreshing...")
            self.refresh_token()
            response = requests.request(method, url, headers=self.headers, **kwargs)
        return response

    def get_user_info(self, username):
        """获取用户对象信息"""
        try:
            url = f"{self.base_url}/users/{username}"
            response = self.request_with_auto_refresh("GET", url)
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Failed to get Zentao user '{username}': {response.status_code} - {response.text}")
        except Exception as e:
            logging.exception(f"Error retrieving Zentao user '{username}': {e}")
        return None

    def delete_user(self, user_id, username):
        """删除禅道用户"""
        try:
            url = f"{self.base_url}/users/{user_id}"
            response = self.request_with_auto_refresh("DELETE", url)

            if response.status_code == 200:
                result = response.json()
                if result.get("message") == "success":
                    logging.info(f"Zentao user '{username}' deleted successfully.")
                else:
                    logging.error(f"Zentao deletion failed for '{username}': {result}")
            else:
                logging.error(f"Failed to delete Zentao user '{username}': {response.status_code} - {response.text}")
        except Exception as e:
            logging.exception(f"Exception while deleting Zentao user '{username}': {e}")

    def process(self, action, user_obj):
        username = user_obj.get("name") or user_obj.get("username")
        if not username:
            logging.warning("Missing 'name' in user object for Zentao")
            return

        if action == "delete-user":
            user_info = self.get_user_info(username)
            if user_info:
                user_id = user_info.get("id")
                if user_id:
                    self.delete_user(user_id, username)
                else:
                    logging.warning(f"No user ID found for Zentao user '{username}'")
        else:
            logging.info(f"ZentaoHandler does not handle action: {action}")

