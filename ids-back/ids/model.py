from django.db import models


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=255, unique=True, null=False)
    password_hash = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.user_name

    class Meta:
        app_label = 'ids'
        db_table = 'Users'


class DataPackets(models.Model):
    packet_id = models.AutoField(primary_key=True)
    packet_name = models.CharField(max_length=100)
    upload_time = models.DateTimeField(auto_now_add=True)
    packet_size = models.IntegerField()

    def __str__(self):
        return self.packet_name

    class Meta:
        app_label = 'ids'
        db_table = 'DataPackets'


class PredictionResults(models.Model):
    predict_id = models.AutoField(primary_key=True)
    predict_name = models.CharField(max_length=100)
    predict_time = models.DateTimeField(auto_now_add=True)
    predict_size = models.IntegerField()

    def __str__(self):
        return self.predict_name

    class Meta:
        app_label = 'ids'
        db_table = 'PredictionResults'
