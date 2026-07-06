from django.db import models

# Create your models here.
class Warehouse (models.Model):
    nom = models.CharField(max_length= 100)
    localisation = models.CharField(max_length= 100)
    capacite = models.IntegerField()
    
    def __str__(self):
        return self.nom


class Product(models.Model):
    
    ETAT = [
        ('disponible','Disponible'),
        ('reserver','Reserver'),
        ('perimer','Perimer')
    ]
    
    
    nom = models.CharField(max_length= 100)
    quantite = models.PositiveIntegerField()    
    etat = models.CharField(max_length= 100 , choices=ETAT, default='disponible')
    date_expiration = models.DateField()
    
    entrepot = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name='produits'
    )
    
    def __str__(self):
        return self.nom
    