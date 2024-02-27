from flask import Flask, jsonify, request
import subprocess
import mysql.connector
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)


# MySQL database connection configuration
db_config = {
    'host': os.environ.get('DB_HOST'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_NAME')
}

@app.route('/applications')
def get_applications():
    try:
        # Establish a connection to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Execute SQL query to fetch distinct application names
        cursor.execute("SELECT DISTINCT app_name FROM deployment_logs")
        applications = [row[0] for row in cursor.fetchall()]  # Fetch all rows and extract app names

        # Close cursor and connection
        cursor.close()
        connection.close()

        return jsonify(applications)
    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500

@app.route('/metrics')
def get_metrics():
    # Retrieve the 'app_name' parameter from the request URL
    app_name = request.args.get('app_name')

    if not app_name:
        return jsonify({"error": "Missing 'app_name' parameter"}), 400

    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Construct the SQL query with the provided 'app_name'
        sql_query = f"""
            SELECT 
                app_name as "app_name",
                COUNT(deployment_count) AS total_deployments,
                SUM(CASE WHEN deployment_status = 'PASS' THEN 1 ELSE 0 END) AS passed_deployments,
                SUM(CASE WHEN deployment_status = 'FAIL' THEN 1 ELSE 0 END) AS failed_deployments
            FROM 
                deployment_logs
            WHERE 
                app_name = '{app_name}';
        """

        # Execute the SQL query
        cursor.execute(sql_query)
        metrics = cursor.fetchone()

        if metrics:
            # Construct a dictionary from the retrieved metrics
            metrics_dict = {
                "app_name":metrics[0],
                "total_deployments": metrics[1],
                "passed_deployments": metrics[2],
                "failed_deployments": metrics[3]
            
            }
            return jsonify(metrics_dict), 200
        else:
            return jsonify({"error": f"No metrics found for app '{app_name}'"}), 404

    except mysql.connector.Error as error:
        return jsonify({"error": f"MySQL error: {error}"}), 500

    finally:
        # Close the database connection
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/insert-record', methods=['POST'])
def insert_record():
    try:
        # Extract parameters from the request body
        data = request.json
        app_name = data.get('app_name')
        deployment_count = data.get('deployment_count')
        deployment_status = data.get('deployment_status')

        if not (app_name and deployment_count and deployment_status):
            return jsonify({"error": "Missing parameters"}), 400

        # Call the update_deployment_logs.py script using subprocess
        process = subprocess.run(['python3', 'update_deployment_logs.py', app_name, str(deployment_count), deployment_status], capture_output=True, text=True)

        # Check the subprocess return code
        if process.returncode == 0:
            return jsonify({"message": process.stdout}), 200
        else:
            return jsonify({"error": process.stderr}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#Display Record 
@app.route('/display-record', methods=['GET'])
def display_record():
    try:
        # Extract parameters from the request body
        data = request.json
        app_name = data.get('app_name')
        #deployment_count = data.get('deployment_count')
        #deployment_status = data.get('deployment_status')

        if not (app_name):
            return jsonify({"error": "Missing parameters"}), 400

        # Call the update_deployment_logs.py script using subprocess
        process = subprocess.run(['python3', 'display_deployments.py', app_name], capture_output=True, text=True)

        # Check the subprocess return code
        if process.returncode == 0:
            return jsonify({"message": process.stdout}), 200
        else:
            return jsonify({"error": process.stderr}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
