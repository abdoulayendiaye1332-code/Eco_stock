from django.shortcuts import render,get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Warehouse,Product
from .serializers import WarehouseSerializer,ProductSerializer


class ProductViewset(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        product = self.get_object()
        # Recuperation de l'id du nouvelle entrepot
        newwarehouse_id= request.data.get('newwarehouse_id') 
        
        # si l'id de l'entrepot a été renseigner
        if not newwarehouse_id:
            return Response({'error':"id de l'entrepot est requis"}, status = 400)
        
        # verification du produit s'il n'est pas perimer
        if product.etat == 'perimer':
            return Response({'error':"impossible de deplacer un produit perimer"},status = 400)
        
        #recuperation de l'entrepot
        newwarehouse= get_object_or_404(Warehouse,newwarehouse_id)
        
        # deplacement et sauvegarde 
        product.entrepot =newwarehouse
        product.save()
        return Response({'status':'produit deplacer avec succes'})
    

class WarehouseViewset(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['get'])
    def audit(self, request, pk=None):
        warehouse = self.get_object()
        product = warehouse.produits
        
        data = {
            'totalproduit': product.count()
        }
        
        return Response(data)
        
    
    
