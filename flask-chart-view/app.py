from flask import Flask, render_template, send_from_directory, jsonify, request, redirect, url_for
import os
import json

app = Flask(__name__)

def format_if_float(value):
    try:
        # Try to convert to float and format
        return f"{float(value):.2f}"
    except ValueError:
        # Return original value if not a float
        return value

# Add custom filter to Jinja2 environment
app.jinja_env.filters['format_if_float'] = format_if_float

# Directory where the HTML files are stored
HTML_FILES_DIR = 'chart-html-files/5min'
JSON_FILES_DIR = 'json-bt-results/5min'

def delete_files(directory):
    for f in os.listdir(directory):
        if f.endswith('.html') or f.endswith('.json'):
            os.remove(os.path.join(directory, f))


@app.route('/')
def index():
    # List all HTML files in the directory
    html_files = [f for f in os.listdir(HTML_FILES_DIR) if f.endswith('.html')]
    # List all JSON files
    json_files = [f for f in os.listdir(JSON_FILES_DIR) if f.endswith('.json')]

    available_values = []
    # Check if there are any JSON files
    if json_files:
        # Read the first JSON file
        with open(os.path.join(JSON_FILES_DIR, json_files[0]), 'r') as file:
            data = json.load(file)
        
        # Extract all values from the JSON data
        for key, value in data.items():
            if isinstance(value, list):
                available_values.extend(key)  # Add all elements from the list
            else:
                available_values.append(key)  # Add single value

    return render_template('index.html', html_files=html_files, json_files=json_files, available_values=available_values)

@app.route('/wipe-data', methods=['GET', 'POST'])
def wipe_data():
    if request.method == 'POST':
        delete_files(HTML_FILES_DIR)
        delete_files(JSON_FILES_DIR)
        return redirect(url_for('index'))

    return render_template('confirm_wipe.html')  # A template to confirm the action

@app.route('/view/<filename>')
def view_html_file(filename):
    # Serve the specific HTML file
    return send_from_directory(HTML_FILES_DIR, filename)


@app.route('/view/json/<filename>')
def view_json_file(filename):
    file_path = os.path.join(JSON_FILES_DIR, filename)
    html_filename = filename.replace('.json', '.html')
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            json_data = json.load(file)
        return render_template('json_viewer_materialize.html', json_data=json_data, html_filename=html_filename)
    else:
        return "File not found", 404
    
@app.route('/analyze')
def analyze_parameter():
    parameter = request.args.get('parameter')

    if not parameter:
        return "Parameter not specified", 400

    values = []
    for file_name in os.listdir(JSON_FILES_DIR):
        if file_name.endswith('.json'):
            file_path = os.path.join(JSON_FILES_DIR, file_name)
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                if parameter in json_data:
                    values.append((file_name, float(json_data[parameter])))

    if not values:
        return f"No data found for parameter: {parameter}", 404

    values.sort(key=lambda x: x[1])  # Sort by parameter value
    top_10_highest = values[-20:]
    top_10_lowest = values[:20]
    median_value = sorted(values, key=lambda x: x[1])[len(values) // 2][1]
    closest_to_median = sorted(values, key=lambda x: abs(x[1] - median_value))[:20]

    return render_template('analysis.html', 
                           parameter=parameter,
                           top_10_highest=top_10_highest, 
                           top_10_lowest=top_10_lowest, 
                           closest_to_median=closest_to_median)


if __name__ == '__main__':
    app.run(debug=True)
