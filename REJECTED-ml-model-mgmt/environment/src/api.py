from flask import Flask

app = Flask(__name__)

# Legacy placeholder kept around so we do not delete files from the task.
# The actual task implementation now belongs in ml_model_mgmt_server.cpp.

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
