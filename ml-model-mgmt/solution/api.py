import csv
import os
import pandas as pd
from flask import Flask, request, jsonify, render_template
from sklearn.preprocessing import StandardScaler

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = '/app/workspace/data'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

processed_df = None


def _looks_like_headerless_csv(raw_csv):
    rows = list(csv.reader(raw_csv.splitlines()))
    if len(rows) < 2:
        return False

    first_row = [cell.strip() for cell in rows[0]]
    second_row = [cell.strip() for cell in rows[1]]

    if len(first_row) != len(second_row):
        return False

    def is_numeric(cell):
        if cell == "":
            return False
        try:
            float(cell)
            return True
        except ValueError:
            return False

    return all(is_numeric(cell) for cell in first_row) and all(
        cell == "" or is_numeric(cell) for cell in second_row
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/v1/data/upload', methods=['POST'])
def upload_data():
    global processed_df
    try:
        # Handle CSV or JSON
        if request.is_json:
            payload = request.get_json(silent=True)
            if not isinstance(payload, list):
                raise ValueError('JSON body must be an array of records')
            df = pd.DataFrame(payload)
        elif request.content_type == 'text/csv':
            from io import StringIO
            raw_csv = request.get_data(as_text=True)
            if not raw_csv.strip():
                raise ValueError('Input data must contain at least one record')
            if _looks_like_headerless_csv(raw_csv):
                raise ValueError('CSV input must include a header row')
            df = pd.read_csv(StringIO(raw_csv))
        else:
            return jsonify({"error": "Unsupported format"}), 415

        if df.empty:
            raise ValueError('Input data must contain at least one record')
        
        # Preprocessing
        df.fillna(df.mean(numeric_only=True), inplace=True)
        scaler = StandardScaler()
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 0:
            df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
            
        # One-hot encoding for categorical
        cat_cols = df.select_dtypes(include=['object']).columns
        if len(cat_cols) > 0:
            df = pd.get_dummies(df, columns=cat_cols)
            
        processed_df = df
        return jsonify({"message": "Data processed successfully", "rows": len(df)}), 200
    except (ValueError, TypeError, KeyError, pd.errors.ParserError) as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Internal error"}), 500

@app.route('/api/v1/data/processed', methods=['GET'])
def get_processed_data():
    global processed_df
    if processed_df is not None:
        return jsonify(processed_df.to_dict(orient='records')), 200
    return jsonify({"error": "No data processed yet"}), 404

@app.route('/api/v1/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        features = data.get('features', [])
        prediction = sum(features) if features else 0
        return jsonify({"prediction": prediction, "status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
