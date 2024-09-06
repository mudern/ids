import json
import os

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

import ids.settings
from ids import settings
from ids.model import DataPackets, PredictionResults


def hello_world(request):
    data = {
        'message': 'Hello, World!'
    }
    return JsonResponse(data)


# 关于数据库的相关操作

@require_http_methods('GET')
def get_data_packets(request):
    # 从数据库中获取所有数据包对象
    data_packets = DataPackets.objects.all()

    # 将数据包对象转换为字典列表
    data_packets_list = []
    for packet in data_packets:
        packet_dict = {
            'packet_id': packet.packet_id,
            'packet_name': packet.packet_name,
            'upload_time': packet.upload_time.strftime("%Y-%m-%d %H:%M:%S") if packet.upload_time else None,
            'packet_size': packet.packet_size
        }
        data_packets_list.append(packet_dict)

    # 返回 JSON 响应
    return JsonResponse(data_packets_list, safe=False)


@require_http_methods(["POST"])
@csrf_exempt
def update_data_packet(request, packet_id):
    import json
    try:
        # 解析请求体中的JSON数据
        data = json.loads(request.body)

        # 查找指定ID的数据包
        packet = DataPackets.objects.get(packet_id=packet_id)

        # 更新字段
        packet.packet_name = data.get('packet_name', packet.packet_name)
        packet.packet_size = data.get('packet_size', packet.packet_size)

        # 保存更改
        packet.save()

        # 返回成功响应
        return JsonResponse({'message': 'Data packet updated successfully'}, status=200)
    except DataPackets.DoesNotExist:
        return JsonResponse({'error': 'Data packet not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["DELETE"])
@csrf_exempt
def delete_data_packet(request, packet_id):
    try:
        # 查找并删除指定ID的数据包
        packet = DataPackets.objects.get(packet_id=packet_id)
        packet_name = DataPackets.objects.get(packet_id=packet_id).packet_name
        packet.delete()
        # 返回成功响应
        # 删除文件
        file_path = os.path.join(ids.settings.IDS_DIR+"\\packets", packet_name)
        if os.path.exists(file_path):
            os.remove(file_path)
        return JsonResponse({'message': 'Data packet deleted successfully'}, status=200)
    except DataPackets.DoesNotExist:
        return JsonResponse({'error': 'Data packet not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def add_data_packet(request):
    try:
        # 获取上传的文件
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'error': 'No file provided'}, status=400)

        # 文件保存路径
        file_path = os.path.join(settings.IDS_DIR+'\\packets', file.name)

        # 保存文件到文件系统
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # 获取文件大小
        file_size = file.size

        # 创建新的数据包实例
        new_packet = DataPackets(
            packet_name=file.name,
            packet_size=file_size,
            upload_time=timezone.now()
        )
        new_packet.save()

        # 返回成功响应
        return JsonResponse({'message': 'Data packet created successfully', 'packet_id': new_packet.packet_id},
                            status=201)
    except KeyError as e:
        return JsonResponse({'error': f'Missing key {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# 关于用户的相关操作

@require_http_methods(["GET"])
def get_users(request):
    users = User.objects.all().values('id', 'username')
    user_list = list(users)
    return JsonResponse(user_list, safe=False)


@require_http_methods(["POST"])
@csrf_exempt
def update_users(request):
    data = json.loads(request.body)
    user_id = data.get('user_id')
    new_username = data.get('user_name')
    print(user_id, new_username)
    if not user_id or not new_username:
        return JsonResponse({"error": "Please provide both id and new username"}, status=400)

    try:
        user = User.objects.get(id=user_id)
        user.username = new_username
        print(user)
        user.save()
        return JsonResponse({"message": "Username updated successfully"}, status=200)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)


@require_http_methods(["DELETE"])
@csrf_exempt
def delete_users(request, user_id):
    if not user_id:
        return JsonResponse({"error": "Please provide user id"}, status=400)

    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return JsonResponse({"message": "User deleted successfully"}, status=200)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)


@require_http_methods(["POST"])
@csrf_exempt
def users_login(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')

    user = authenticate(username=username, password=password)
    print(user)
    if user is not None:
        if user.is_active:
            login(request, user)
            response = HttpResponse()
            return response
        else:
            return JsonResponse({"error": "User account is disabled"}, status=401)
    else:
        return JsonResponse({"error": "Invalid credentials"}, status=401)


@require_http_methods(["POST"])
@csrf_exempt
def users_register(request):
    data = json.loads(request.body)
    username = data.get('user_name')
    password = data.get('password')
    if not username or not password:
        return JsonResponse({"error": "Please provide both username and password"}, status=400)

    User.objects.create_user(username=username, password=password)
    return JsonResponse({"message": "User registered successfully"}, status=201)


@require_http_methods(["GET"])
@csrf_exempt
@permission_classes([IsAuthenticated])
def get_logged_in_user(request):
    user_data = {
        'id': request.user.id,
        'username': request.user.username
    }
    print(user_data)
    return JsonResponse(user_data)


# 关于预测结果

@require_http_methods('GET')
def get_prediction_results(request):
    # 从数据库中获取所有预测结果对象
    prediction_results = PredictionResults.objects.all()

    # 将预测结果对象转换为字典列表
    prediction_results_list = []
    for prediction in prediction_results:
        prediction_dict = {
            'predict_id': prediction.predict_id,
            'predict_name': prediction.predict_name,
            'predict_time': prediction.predict_time.strftime("%Y-%m-%d %H:%M:%S") if prediction.predict_time else None,
            'predict_size': prediction.predict_size
        }
        prediction_results_list.append(prediction_dict)

    # 返回 JSON 响应
    return JsonResponse(prediction_results_list, safe=False)


@require_http_methods(["DELETE"])
@csrf_exempt
def delete_prediction_result(request, predict_id):
    try:
        # 查找并删除指定 ID 的预测结果
        prediction = PredictionResults.objects.get(predict_id=predict_id)
        prediction_name = PredictionResults.objects.get(predict_id=predict_id).predict_name
        prediction.delete()

        # 返回成功响应
        # 删除文件
        file_path = os.path.join(settings.IDS_DIR+"cnn_model/static/predict", prediction_name)  # 替换为实际路径
        if os.path.exists(file_path):
            os.remove(file_path)

        return JsonResponse({'message': 'Prediction result deleted successfully'}, status=200)
    except PredictionResults.DoesNotExist:
        return JsonResponse({'error': 'Prediction result not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@csrf_exempt
def get_prediction_table(request):
    file_path = settings.IDS_DIR+"/cnn_model/static/result/predict_data.json"
    try:
        with open(file_path, 'r') as file:
            predict_data = json.load(file)
        return JsonResponse(predict_data, safe=False)
    except FileNotFoundError:
        return JsonResponse({'error': 'Predict data file not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@csrf_exempt
def get_prediction_chart(request):
    # 指定路径下的四个 JSON 文件
    files = [
        "attack_type_map.json",
        "connection_status_map.json",
        "protocol_type_map.json",
        "service_type_map.json"
    ]

    # 存储结果的字典
    result = {}

    try:
        # 遍历每个 JSON 文件
        for file_name in files:
            file_path = os.path.join(
                settings.IDS_DIR+"/cnn_model/static/result", file_name)
            # 检查文件是否存在
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    result[file_name.split('.')[0]] = data
            else:
                result[file_name.split('.')[0]] = None
        return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
