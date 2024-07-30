from django.db import models
from accounts.models import User, Landmark

# Create your models here.
class CropRecommendation(models.Model):
    cropId = models.BigAutoField(primary_key=True, editable=False) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    landId = models.ForeignKey(Landmark, on_delete=models.CASCADE)
    N=models.PositiveIntegerField()
    P=models.PositiveIntegerField()
    K=models.PositiveIntegerField()
    temperature=models.FloatField(blank=True,null=True)
    humidity=models.FloatField(blank=True,null=True)
    ph=models.FloatField(blank=True,null=True)
    rainfall=models.FloatField(blank=True,null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    prediction=models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.first_name}"
    
class PreviousCropRequest(models.Model):
    requestId = models.BigAutoField(primary_key=True, editable=False) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    landId = models.ForeignKey(Landmark, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    season = models.CharField(max_length=20)
    month = models.PositiveIntegerField()
    crop = models.CharField(max_length=100)
    area = models.FloatField()
    production = models.FloatField(blank=True, null=True)
    yield_per_hectare = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request ID: {self.requestId}, User: {self.user.username}, Land: {self.landId}, Year: {self.year}, Crop: {self.crop}"