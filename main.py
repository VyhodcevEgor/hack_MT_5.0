from flask import Flask, jsonify, request, abort, json
from Database import database_requests

app = Flask(__name__)


def error_404(description):
    response = app.response_class(
        response=json.dumps({"description": description}),
        status=404,
        mimetype='application/json'
    )
    return response


def error_500(description):
    response = app.response_class(
        response=json.dumps({"description": description}),
        status=500,
        mimetype='application/json'
    )
    return response


def status_200(data):
    response = app.response_class(
        response=json.dumps({"result": data}),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/hack/API/v1.0/get_extended_info', methods=['GET'])
def get_extended_info():
    args = dict(request.args)
    if not args or 'id' not in args:
        abort(400)

    bank_info = []
    query_result = database_requests.get_extended_info(args.get('id'))
    predicted_time = database_requests.predict_time(args.get('id'))
    if query_result:
        bank_info.append(
            {
                'bank_name': query_result[0][0],
                'services': query_result[0][1],
                'work_hours': query_result[0][2],
                'latitude': query_result[0][3],
                'longitude': query_result[0][4],
                'load_type': query_result[0][5],
                'ext_work_hours': query_result[1],
                'predicted_time': predicted_time
            }
        )

        response_to_send = app.response_class(
            response=json.dumps(bank_info),
            status=200,
            mimetype='application/json'
        )
        return response_to_send
    else:
        abort(400)


@app.route('/hack/API/v1.0/banks_in_radius', methods=['GET'])
def get_banks_in_radius():
    args = dict(request.args)
    if not args or 'currentPosition' not in args:
        return error_404('Current user position missing')

    service = args.get("service")
    loading_type = args.get("loadingType")
    distance = args.get("distance")
    lat, lng = map(float, args.get("currentPosition").split())
    data = {"banks": database_requests.get_banks_in_radius(lat, lng, service, loading_type, distance)}

    return status_200(data)


@app.route('/hack/API/v1.0/history', methods=['GET', "POST", "DELETE"])
def get_history():
    if request.method == 'GET':
        data = database_requests.get_history()
        return status_200(data)

    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'bank_id' not in data:
            return error_404('missing bank_id')
        try:
            database_requests.insert_history(data['bank_id'])
        except Exception as e:
            print(e)
            return error_500('internal server error')
        return status_200('success')

    elif request.method == 'DELETE':
        data = request.get_json()
        if not data or 'bank_id' not in data:
            return error_404('missing bank_id')
        try:
            database_requests.delete_history(data['bank_id'])
        except Exception as e:
            print(e)
            return error_500('internal server error')
        return status_200('success')

    else:
        return 'Method not allowed', 405


if __name__ == '__main__':
    app.run(debug=True)
