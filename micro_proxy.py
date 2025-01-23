from flask import Flask, request, jsonify
from flask_basicauth import BasicAuth
import json
import requests

app = Flask(__name__)

# Configure basic auth
app.config['BASIC_AUTH_USERNAME'] = 'john'
app.config['BASIC_AUTH_PASSWORD'] = 'matrix'
basic_auth = BasicAuth(app)

# Load GLPI authorization configuration once at startup
with open('data.json') as json_file:
    authorization = json.load(json_file)

# Extract the GLPI base URL from the JSON file, e.g. "http://YOUR_GLPI_IP/apirest.php"
GLPI_BASE_URL = authorization.get('glpi_url')

@app.route('/glpi', methods=['POST'])
@basic_auth.required
def create_glpi_ticket():
    """Create a new GLPI ticket using data from the request JSON body."""
    # Parse the incoming JSON request
    data = request.get_json()

    # Prepare headers for initializing GLPI session
    headers_init = {
        'Content-Type': 'application/json',
        'Authorization': authorization['user_token'],
        'App-Token': authorization['app_token']
    }

    try:
        # Initialize session
        session_response = requests.get(
            f'{GLPI_BASE_URL}/initSession',
            headers=headers_init
        )
        session_response.raise_for_status()  # Raise an error for 4XX/5XX responses

        session_data = session_response.json()
        session_token = session_data.get("session_token")

        if not session_token:
            # If GLPI doesn't return a session token, return a 401 or a suitable status
            return jsonify(success=False, message="No session token returned."), 401

        # Prepare headers with the session token
        headers_with_session = {
            'App-Token': authorization['app_token'],
            'Session-Token': session_token,
            'Content-Type': 'application/json'
        }

        # Create the ticket
        create_response = requests.post(
            f'{GLPI_BASE_URL}/Ticket/',
            headers=headers_with_session,
            json=data
        )

        # Kill the session to clean up
        requests.get(
            f'{GLPI_BASE_URL}/killSession',
            headers=headers_with_session
        )

        # Determine success based on the response status
        success = (create_response.status_code == 201)

        return jsonify(
            success=success,
            response_text=create_response.text
        ), create_response.status_code

    except requests.exceptions.RequestException as req_err:
        # Handle network or request errors
        return jsonify(success=False, error=str(req_err)), 500

    except Exception as e:
        # Catch-all for any other runtime errors
        return jsonify(success=False, error=str(e)), 500


if __name__ == '__main__':
    app.run(debug=True)
