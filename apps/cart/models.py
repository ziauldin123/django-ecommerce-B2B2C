from statistics import mode
from django.db import models

# Create your models here.


class District(models.Model):
    district = models.CharField(max_length=32)

    def __str__(self):
        return self.district


class Sector(models.Model):
    sector = models.CharField(max_length=32)

    district = models.ForeignKey(District, on_delete=models.CASCADE)

    def __str__(self):
        return self.sector


class Cell(models.Model):
    cell = models.CharField(max_length=32)

    district = models.ForeignKey(District, on_delete=models.CASCADE)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)

    def __str__(self):
        return self.cell


class Village(models.Model):
    village = models.CharField(max_length=32)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE)

    def __str__(self):
        return self.village


class MobileOperator(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name