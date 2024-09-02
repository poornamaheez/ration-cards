from flask import Flask, request, jsonify, render_template
from table import rationCardTables
from datetime import datetime

app = Flask(__name__)

@app.route('/test')
def home():
    return "Welcome to the Flask app!"

@app.route('/show', methods=['POST'])
def renderTable():
    try:
        # Check the Content-Type of the request
        content_type = request.headers.get('Content-Type')
        
        if content_type == 'application/json':
            # Get JSON data
            form_data = request.json
        elif content_type == 'application/x-www-form-urlencoded':
            # Get form data from URL-encoded form
            form_data = {
                "month": request.form.get("month"),
                "year": request.form.get("year"),
                "shop_no": request.form.get("shop_no"),
                "type": request.form.get("type")
            }
        else:
            return jsonify({"error": "Unsupported Media Type: Please send data as JSON or form-encoded."}), 415
        
        if not form_data:
            return jsonify({"error": "No form data provided"}), 400

        # Call the function with the provided form data
        result_data = rationCardTables(form_data)
        
        # Create response
        result = {"status": "success", "data": result_data}
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def show_form():
    current_year = datetime.now().year
    current_month = datetime.now().month
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    return render_template('form.html', current_year=current_year, current_month=current_month, month_names=month_names)

if __name__ == '__main__':
    app.run()
