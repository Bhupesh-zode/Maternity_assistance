from django.db import models
class Dataset(models.Model):
    data_id=models.AutoField(primary_key=True)
    data_set = models.FileField(upload_to='datasetfile')
    xg_accuracy = models.FloatField(null=True)
    xg_precision = models.FloatField(null=True)
    xg_recall = models.FloatField(null=True)
    xg_f1_score = models.FloatField(null=True)
    xg_algo = models.CharField(max_length=500,null=True)
    ad_accuracy = models.FloatField(null=True)
    ad_precision = models.FloatField(null=True)
    ad_recall = models.FloatField(null=True)
    ad_f1_score = models.FloatField(null=True)
    ad_algo = models.CharField(max_length=500,null=True)
    lr_accuracy = models.FloatField(null=True)
    lr_precision = models.FloatField(null=True)
    lr_recall = models.FloatField(null=True)
    lr_f1_score = models.FloatField(null=True)
    lr_algo = models.CharField(max_length=500,null=True)
    class Meta:
        db_table = 'dataset_details'


class Algorithms(models.Model):
    algo_id=models.AutoField(primary_key=True)
    algo_name=models.CharField(max_length=100,null=True)
    accuracy=models.CharField(max_length=500,null=True)
    precision=models.CharField(max_length=500,null=True)
    recall=models.CharField(max_length=500,null=True)
    f1_score=models.CharField(max_length=500,null=True)


    class Meta:
        db_table='Algorithms_details'
        
# Create your models here.
