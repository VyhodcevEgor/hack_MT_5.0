from flask import Flask, jsonify, request, abort, json
from Database import database_requests
from flask_cors import CORS
from datetime import datetime
from random import choice

app = Flask(__name__)
CORS(app)


def error_404(description):
    # Создание объекта ответа с кодом 404 и описанием ошибки
    response = app.response_class(
        response=json.dumps({"description": description}),
        status=404,
        mimetype='application/json'
    )
    return response


def error_500(description):
    # Создание объекта ответа с кодом 500 и описанием ошибки
    response = app.response_class(
        response=json.dumps({"description": description}),
        status=500,
        mimetype='application/json'
    )
    return response


def status_200(data):
    # Создание объекта ответа с кодом 200 и описанием ошибки
    response = app.response_class(
        response=json.dumps({"result": data}),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/hack/API/v1.0/get_extended_info', methods=['GET'])
def get_extended_info():
    args = dict(request.args)
    if not args or 'id' not in args or "type" not in args:
        abort(400)
    branch_type = args.get("type")
    query_result = None
    if branch_type == "bank":
        # Если тип филиала - банк, получаем расширенную информацию о банке по его идентификатору
        bank_id = int(args.get('id'))
        query_result = database_requests.get_extended_info(bank_id)
    elif branch_type == "atm":
        # Если тип филиала - банкомат, получаем расширенную информацию о банкомате по его идентификатору
        atm_id = int(args.get('id'))
        query_result = database_requests.get_atm_extended_info(atm_id)

    if query_result:
        response_to_send = app.response_class(
            response=json.dumps(query_result),
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
    bank_info = database_requests.get_banks_in_radius(lat, lng, service, loading_type, distance)
    banks = bank_info['banks']
    branches = []
    cur_time = int(datetime.now().strftime("%H"))
    for bank in banks:
        print(bank)
        bank_id = bank['bankId']
        load_data = bank['loadType']
        # status = bank['status']
        current_time_load = 0
        # Прогнозируем загрузку на 10, 13 и 16 часов дня
        if cur_time < 10:
            current_time_load = load_data.get('10')
        elif cur_time < 13:
            current_time_load = load_data.get('13')
        else:
            current_time_load = load_data.get('16')
        # Создаем информацию о филиале и добавляем в список
        branches.append(
            {
                'id': bank_id,
                'congestion': int(current_time_load / 60 * 100),    # Рассчитываем загруженность в процентах
                # 60 - текущая мода для всех отделений
                "travel_distance": database_requests.haversine(lat, lng, float(bank['latitude']), float(bank['longitude'])),
            }
        )
    min_travel_distance = min(branch['travel_distance'] for branch in branches)
    max_travel_distance = max(branch['travel_distance'] for branch in branches)

    # Задаем веса для расстояния путешествия и загруженности (Тут можно интегрировать машинное обучение)
    travel_distance_weight = 0.6
    congestion_weight = 0.4
    # Если список филиалов пуст, выбираем случайный банк
    if len(branches) == 0:
        optimal_branch = choice(banks)['bankId']
    # Если в списке только один филиал, выбираем его
    elif len(branches) == 1:
        optimal_branch = banks[-1]['bankId']
    else:
        # Рассчитываем оценку для каждого филиала на основе весов и нормализованных значений
        for branch in branches:
            normalized_travel_distance = (branch['travel_distance'] - min_travel_distance) / (
                        max_travel_distance - min_travel_distance)
            normalized_congestion = branch['congestion'] / 100.0

            score = (normalized_travel_distance * travel_distance_weight) + (normalized_congestion * congestion_weight)
            branch['score'] = score

        # Находим филиал с наименьшей оценкой
        optimal_branch = min(branches, key=lambda x: x['score'])
        optimal_branch = optimal_branch['id']

    # Добавляем информацию о выбранном оптимальном филиале в результат
    bank_info['optimal_branch'] = optimal_branch
    print(branches)
    return status_200(bank_info)


if __name__ == '__main__':
    app.run(debug=True)
