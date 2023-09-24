from flask import Flask, jsonify, request, abort
from Database import database_requests

app = Flask(__name__)


@app.route('/hack/API/v1.0/get_extended_info', methods=['POST'])
def get_extended_info():
    if not request.json or 'id' not in request.json:
        abort(400)

    bank_info = []
    query_result = database_requests.get_extended_info(request.json['id'])
    if query_result:
        bank_info.append(
            {
                'bank_name': query_result[0],
                'services': query_result[1],
                'work_hours': query_result[2],
                'latitude': query_result[3],
                'longitude': query_result[4],
                'load_type': query_result[5]
            }
        )

        return jsonify({'response': {'bank_info': bank_info}})
    else:
        abort(400)


if __name__ == '__main__':
    app.run(debug=True)
