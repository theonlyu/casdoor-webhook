import requests
import logging
from requests.auth import HTTPBasicAuth

class GrafanaHandler:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.auth = HTTPBasicAuth(username, password)
        self.headers = {
            "Accept": "application/json"
        }

    def get_user_id(self, username):
        """通过用户名查找 Grafana 用户 ID"""
        url = f"{self.base_url}/users/lookup?loginOrEmail={username}"
        try:
            response = requests.get(url, headers=self.headers, auth=self.auth)
            if response.status_code == 200:
                return response.json().get("id")
            elif response.status_code == 404:
                logging.warning(f"Grafana user '{username}' not found.")
                return None
            else:
                logging.error(f"Failed to lookup Grafana user '{username}': {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logging.exception(f"Exception while looking up Grafana user '{username}': {str(e)}")
            return None

    def delete_user(self, user_id, username_for_log):
        url = f"{self.base_url}/admin/users/{user_id}"
        try:
            response = requests.delete(url, headers=self.headers, auth=self.auth)
            if response.status_code == 200:
                logging.info(f"Grafana user '{username_for_log}' deleted successfully.")
            else:
                logging.error(f"Failed to delete Grafana user '{username_for_log}': {response.status_code} - {response.text}")
        except Exception as e:
            logging.exception(f"Exception while deleting Grafana user '{username_for_log}': {str(e)}")

    def process(self, action, user_obj):
        if action != "delete-user":
            logging.info("GrafanaHandler only handles delete-user action.")
            return

        username = user_obj.get("name") or user_obj.get("username")
        if not username:
            logging.warning("Missing 'name' in user object for Grafana.")
            return

        user_id = self.get_user_id(username)
        if user_id:
            self.delete_user(user_id, username)

