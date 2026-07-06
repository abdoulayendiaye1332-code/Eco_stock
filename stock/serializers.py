from rest_framework import serializers
from .models import Warehouse,Product


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields= ['id','nom','localisation','capacite']
  
  
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','nom','quantite','etat','date_expiration','entrepot']   
        
        
        
   