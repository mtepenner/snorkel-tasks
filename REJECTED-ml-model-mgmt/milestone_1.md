# milestone 1: get the data preprocessing api running in `/app/workspace/src/ml_model_mgmt_server.cpp`

- stand up a C++ HTTP service on port `8000`.
- wire up a POST `/api/v1/data/upload` endpoint to accept either json arrays of objects or raw csv text with a real header row.
- reject empty json/csv, malformed json, and headerless csv with `400`. reject unsupported content types like xml with `415` instead of silently accepting them or falling back to a generic `400`.
- validate the data so garbage input returns `400` or `415`, never a `500`.
- add the preprocessing pass: mean imputation for missing numeric values, standard scaling for numeric columns, and one-hot encoding for categorical columns.
- after encoding categoricals, do not leave the original string columns hanging around.
- slap a GET `/api/v1/data/processed` endpoint on there to spit out the cleaned dataset as a flat json array of row objects with scaled numeric values plus indicator columns.

