FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 拷贝依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝项目代码
COPY . .

# 设置环境变量文件路径（可选）
ENV CONFIG_FILE=config.yaml

# Gunicorn 启动，绑定 0.0.0.0:8000，主模块为 app.py 中的 app 对象
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]

