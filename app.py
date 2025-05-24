from flask import Flask, request, jsonify
import logging
import json  # ✅ 添加导入
from user_sync_handler import get_handlers, load_config

app = Flask(__name__)

logging.basicConfig(
    filename='logs/webhook.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

config = load_config()
handlers = get_handlers(config)

@app.route('/casdoor-webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    action = data.get("action")
    raw_object = data.get("object")  # ⚠️ 这个可能是 str 或 dict

    # ✅ 自动判断类型并解析
    try:
        user_obj = json.loads(raw_object) if isinstance(raw_object, str) else raw_object
    except Exception as e:
        logging.exception("Invalid 'object' JSON format")
        return jsonify({"error": "Invalid 'object' JSON format"}), 400

    if not action or not user_obj:
        return jsonify({"error": "Invalid payload"}), 400

    for handler in handlers:
        try:
            handler.process(action, user_obj)
        except Exception as e:
            logging.exception(f"Handler error: {str(e)}")

    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

