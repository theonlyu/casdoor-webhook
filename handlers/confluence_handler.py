import requests
import logging
import json

class ConfluenceHandler:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

    def delete_user(self, username):
        url = f"{self.base_url}/admin/user/{username}"
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code == 202:
                logging.info(f"Confluence user '{username}' deleted successfully.")
            else:
                logging.error(f"Failed to delete Confluence user '{username}': {response.status_code} - {response.text}")
        except Exception as e:
            logging.exception(f"Exception while deleting Confluence user '{username}': {str(e)}")

    def disable_user(self, username):
        url = f"{self.base_url}/admin/user/{username}/disable"
        try:
            response = requests.put(url, headers=self.headers)
            if response.status_code == 204:
                logging.info(f"Confluence User '{username}' disabled successfully.")
            else:
                logging.error(f"Failed to disable Confluence user '{username}': {response.status_code} - {response.text}")
        except Exception as e:
            logging.exception(f"Exception while disabling Confluence user '{username}': {str(e)}")

    def enable_user(self, username):
        url = f"{self.base_url}/admin/user/{username}/enable"
        try:
            response = requests.put(url, headers=self.headers)
            if response.status_code == 204:
                logging.info(f"Confluence user '{username}' enabled successfully.")
            else:
                logging.error(f"Failed to enable Confluence user '{username}': {response.status_code} - {response.text}")
        except Exception as e:
            logging.exception(f"Exception while enabling Confluence user '{username}': {str(e)}")

    def process(self, action, user_obj):
        username = user_obj.get("name")
        if not username:
            logging.warning("Missing 'name' in user object for Confluence")
            return

        if action == "delete-user":
            self.delete_user(username)
        elif action == "update-user":
            if user_obj.get("isForbidden", False):
                self.disable_user(username)
            else:
                self.enable_user(username)
        else:
            logging.warning(f"Unsupported action: {action}")

