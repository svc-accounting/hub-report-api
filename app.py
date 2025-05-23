from flask import Flask, request, send_file, render_template_string
import pandas as pd
import os

app = Flask(__name__)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/')
def index():
    return "<h2>HUB Report Generator API</h2><p>Go to <a href='/upload'>/upload</a> to use the form.</p>"

@app.route('/upload', methods=['GET'])
def upload_form():
    return render_template_string("""
    <h2>Upload Files to Generate HUB Report</h2>
    <form method="POST" action="/generate-hub" enctype="multipart/form-data">
      OQ File: <input type="file" name="expenditure"><br><br>
      Citibank File: <input type="file" name="citibank"><br><br>
      <input type="submit" value="Generate HUB Report">
    </form>
    """)

@app.route('/generate-hub', methods=['POST'])
def generate_hub():
    expenditure = request.files['expenditure']
    citibank = request.files['citibank']

    exp_path = os.path.join(UPLOAD_DIR, expenditure.filename)
    cit_path = os.path.join(UPLOAD_DIR, citibank.filename)
    expenditure.save(exp_path)
    citibank.save(cit_path)

    df1 = pd.read_excel(exp_path)
    df2 = pd.read_excel(cit_path)

    def format_row(agency, vid, name, obj_code, amount, record_type):
        return f"{str(agency).zfill(5)}{str(vid)[:11].ljust(11)}{str(name).upper().ljust(20)[:20]}{str(obj_code).zfill(4)}{f'{float(amount):012.2f}'.replace('.', '')}{record_type}"

    def extract(df, rtype):
        return [format_row("731", row["TINS No"], row["Short Name"], row["Object Code"], row["Total Paid Amount"], rtype) for _, row in df.iterrows()]

    records = extract(df1, "N") + extract(df2, "H")

    output_file = os.path.join(UPLOAD_DIR, "731_FY25_SemiAnnual.txt")
    with open(output_file, "w") as f:
        f.write("\n".join(records))

    return send_file(output_file, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
