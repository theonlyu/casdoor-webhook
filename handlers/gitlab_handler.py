import requests
import logging

class GitlabHandler:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.headers = {"Authorization": f"Bearer {token}"}

    def get_user_id(self, username):
        """根据用户名搜索 GitLab 用户 ID"""
        try:
            response = requests.get(
                f"{self.base_url}/users?search={username}",
                headers=self.headers
            )
            if response.status_code != 200:
                logging.error(f"Failed to search user '{username}' in GitLab: {response.status_code}")
                return None

            users = response.json()
            if not users:
                logging.warning(f"GitLab user not found: {username}")
                return None

            return users[0]["id"]
        except Exception as e:
            logging.exception(f"Error retrieving GitLab user ID for '{username}': {e}")
            return None

    def delete_user(self, username):
        user_id = self.get_user_id(username)
        if not user_id:
            return

        try:
            response = requests.delete(f"{self.base_url}/users/{user_id}", headers=self.headers)
            if response.status_code == 204:
                logging.info(f"GitLab user '{username}' deleted successfully.")
            else:
                logging.error(f"Failed to delete GitLab user '{username}': {response.status_code} - {response.text}")
        except Exception as e:
            logging.exception(f"Exception while deleting GitLab user '{username}': {e}")

    def block_user(self, username):
        user_id = self.get_user_id(username)
        if not user_id:
            return

        try:
            response = requests.post(f"{self.base_url}/users/{user_id}/block", headers=self.headers)
            if response.status_code == 201:
                logging.info(f"GitLab user '{username}' blocked successfully.")
            else:
                logging.error(f"Failed to block GitLab user '{username}': {response.status_code} - {response.text}")
        except Exception as e:
            logging.exception(f"Exception while blocking GitLab user '{username}': {e}")

    def unblock_user(self, username):
        user_id = self.get_user_id(username)
        if not user_id:
            return

        try:
            response = requests.post(f"{self.base_url}/users/{user_id}/unblock", headers=self.headers)
            if response.status_code == 201:
                logging.info(f"GitLab user '{username}' unblocked successfully.")
            else:
                logging.error(f"Failed to unblock GitLab user '{username}': {response.status_code} - {response.text}")
        except Exception as e:
            logging.exception(f"Exception while unblocking GitLab user '{username}': {e}")

    def process(self, action, user_obj):
        username = user_obj.get("name")
        if not username:
            logging.warning("Missing 'name' in user object for GitLab")
            return

        if action == "delete-user":
            self.delete_user(username)
        elif action == "update-user":
            if user_obj.get("isForbidden", False):
                self.block_user(username)
            else:
                self.unblock_user(username)
        else:
            logging.warning(f"Unsupported action: {action}")

