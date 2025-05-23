from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def format_row(agency, vid, name, obj_code, amount, record_type):
    return f"{str(agency).zfill(5)}{str(vid)[:11].ljust(11)}{str(name).upper().ljust(20)[:20]}{str(obj_code).zfill(4)}{f'{float(amount):012.2f}'.replace('.', '')}{record_type}"

@app.route('/generate-hub', methods=['POST'])
def generate_hub():
    files = request.files
    oq_file = files.get('expenditure')
    citi_file = files.get('citibank')

    if not oq_file or not citi_file:
        return jsonify({'error': 'Both files (expenditure, citibank) are required'}), 400

    oq_path = os.path.join(UPLOAD_DIR, oq_file.filename)
    citi_path = os.path.join(UPLOAD_DIR, citi_file.filename)
    oq_file.save(oq_path)
    citi_file.save(citi_path)

    oq_df = pd.read_excel(oq_path)
    citi_df = pd.read_excel(citi_path)

    def extract_records(df, record_type):
        rows = []
        for _, r in df.iterrows():
            try:
                rows.append(format_row("731", r["TINS No"], r["Short Name"], r["Object Code"], r["Total Paid Amount"], record_type))
            except:
                continue
        return rows

    records = extract_records(oq_df, "N") + extract_records(citi_df, "H")
    output_file = os.path.join(UPLOAD_DIR, "731_FY25_SemiAnnual.txt")

    with open(output_file, "w") as f:
        f.write('\n'.join(records))

    return jsonify({'message': 'HUB report generated', 'file': output_file}), 200

if __name__ == "__main__":
    app.run(debug=True)
