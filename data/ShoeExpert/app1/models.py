from django.db import models

# Create your models here.
class Shoe(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name

class RunningShoe(models.Model):
    shoe_name = models.CharField(max_length=128)
    arch_type = models.CharField(max_length=32, blank=True, null=True)
    brand = models.CharField(max_length=32, blank=True, null=True)
    cushioning = models.CharField(max_length=32, blank=True, null=True)
    distance = models.CharField(max_length=128, blank=True, null=True)
    features = models.CharField(max_length=256, blank=True, null=True)
    flexibility = models.CharField(max_length=32, blank=True, null=True)
    forefoot_height = models.CharField(max_length=8, blank=True, null=True)
    heel_height = models.CharField(max_length=8, blank=True, null=True)
    heel_toe_drop = models.CharField(max_length=8, blank=True, null=True)
    msrp = models.CharField(max_length=8, blank=True, null=True)
    pronation = models.CharField(max_length=256, blank=True, null=True)
    release_date = models.CharField(max_length=128, blank=True, null=True)
    strike_pattern = models.CharField(max_length=128, blank=True, null=True)
    technology = models.CharField(max_length=128, blank=True, null=True)
    terrain = models.CharField(max_length=32, blank=True, null=True)
    toebox = models.CharField(max_length=32, blank=True, null=True)
    use = models.CharField(max_length=128, blank=True, null=True)
    waterproofing = models.CharField(max_length=32, blank=True, null=True)
    weight = models.CharField(max_length=8, blank=True, null=True)
    width = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name
