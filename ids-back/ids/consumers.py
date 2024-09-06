import asyncio
import json
import os

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from cnn_model.model.analysis import analysis
from cnn_model.model.convert import convert
from cnn_model.model.model_torch_socket import train
from cnn_model.model.predict import predict
from ids import settings
from ids.model import PredictionResults


async def save_prediction_result(file_name):
    predict_file_path = os.path.join(settings.IDS_DIR + "/cnn_model/static/predict/" + file_name)
    # 使用 sync_to_async 包装同步的数据库操作
    check_exists = sync_to_async(PredictionResults.objects.filter(predict_name=file_name).exists)
    if not await check_exists():
        new_record = PredictionResults(
            predict_name=file_name,
            predict_size=os.path.getsize(predict_file_path)
        )
        # 使用 sync_to_async 来保存记录，并直接固定参数
        save_record = sync_to_async(
            lambda: new_record.save(
                force_insert=False,
                force_update=False,
                using='default',
                update_fields=None
            ),
            thread_sensitive=True
        )
        await save_record()  # 调用时无需传递参数
        print("记录已保存到数据库")


class TrainConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await train(self)  # 调用train函数，并传入WebSocket连接

    async def disconnect(self, close_code):
        # 这里可以记录断开的原因，如日志输出等
        print(f"Disconnected with close_code: {close_code}")

    async def receive(self, text_data=None, bytes_data=None):
        # 此示例中不需要处理从客户端接收的任何数据
        pass


class PredictConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        # 这里可以记录断开的原因，如日志输出等
        print(f"Disconnected with close_code: {close_code}")

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            await self.send(json.dumps(
                {
                    'type': "message",
                    'message': "开始进行预测,时间较长请勿关闭"
                }
            ))
            print("开始进行预测,时间较长请勿关闭")
            await self.send(json.dumps(
                {
                    'type': "message",
                    'message': "进行格式归一转换"
                }
            ))
            print("进行格式归一转换")
            await asyncio.sleep(0.1)
            convert(text_data)
            await self.send(json.dumps(
                {
                    'type': "message",
                    'message': "正在进行关系转接"
                }
            ))
            print("正在进行关系转接")
            await self.send(json.dumps(
                {
                    'type': "message",
                    'message': "开始启动预测"
                }
            ))
            print("开始启动预测")
            await asyncio.sleep(1)
            predict(text_data, self)
            await self.send(json.dumps(
                {
                    'type': "close",
                    'close': "预测成功完成"
                }
            ))
            await save_prediction_result(text_data)
            await asyncio.sleep(1)
            print("预测成功完成")


class AnalysisConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        # 这里可以记录断开的原因，如日志输出等
        print(f"Disconnected with close_code: {close_code}")

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            await self.send(json.dumps(
                {
                    'type': "message",
                    'message': "开始进行分析,时间较长请勿关闭"
                }
            ))
            await asyncio.sleep(0.1)
            print("开始进行分析,时间较长请勿关闭")
            print("进行预测表格生成")
            await analysis(text_data, self)
            print("预测成功完成")
