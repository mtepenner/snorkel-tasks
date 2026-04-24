import os
import pandas as pd
from flask import Flask, request, jsonify, render_template
from sklearn.preprocessing import StandardScaler

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = '/app/workspace/data'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

processed_df = None

# MILESTONE 2: Web GUI
@app.route('/')
def index():
    return render_template('index.html')

# MILESTONE 1: Preprocessing Upload
@app.route('/api/v1/data/upload', methods=['POST'])
def upload_data():
    global processed_df
    try:
        if request.is_json:
            df = pd.DataFrame(request.json)
        else:
            return jsonify({"error": "Unsupported format"}), 400
        
        # Basic preprocessing (Fill NA and Scale)
        df.fillna(df.mean(numeric_only=True), inplace=True)
        scaler = StandardScaler()
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 0:
            df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
            
        processed_df = df
        return jsonify({"message": "Data processed successfully", "rows": len(df)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# MILESTONE 1: Fetch Processed Data
@app.route('/api/v1/data/processed', methods=['GET'])
def get_processed_data():
    global processed_df
    if processed_df is not None:
        return jsonify(processed_df.to_dict(orient='records')), 200
    return jsonify({"error": "No data processed yet"}), 404

# MILESTONE 3: Model Inference
@app.route('/api/v1/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        features = data.get('features', [])
        # Dummy prediction logic (sum of features)
        prediction = sum(features) if features else 0
        return jsonify({"prediction": prediction, "status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
