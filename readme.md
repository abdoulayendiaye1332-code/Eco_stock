ECO_STOCK_DRF

API REST de gestion de stock (entrepôts + produits) construite avec Django et Django REST Framework (DRF).

Le projet permet de :


Gérer des entrepôts (Warehouse) : nom, localisation, capacité.
Gérer des produits (Product) rattachés à un entrepôt : quantité, état (disponible / réservé / périmé), date d'expiration.
Déplacer un produit d'un entrepôt vers un autre (move).
Auditer un entrepôt pour connaître le nombre total de produits qu'il contient (audit).



1. Structure du projet

ECO_STOCK_DRF/
├── config/                 # Configuration globale du projet Django
│   ├── __init__.py
│   ├── asgi.py              # Point d'entrée ASGI (serveurs async)
│   ├── settings.py          # Réglages du projet (apps, DB, middlewares, DRF...)
│   ├── urls.py               # Routeur principal, inclut les urls de l'app "stock"
│   └── wsgi.py                # Point d'entrée WSGI (serveurs classiques)
│
├── stock/                  # Application métier principale
│   ├── migrations/          # Historique des migrations de la base de données
│   ├── __init__.py
│   ├── admin.py               # Enregistrement des modèles dans l'admin Django
│   ├── apps.py                 # Config de l'application "stock"
│   ├── models.py                # Modèles Warehouse et Product
│   ├── serializers.py            # Sérialiseurs DRF (conversion modèle <-> JSON)
│   ├── tests.py                    # Tests unitaires
│   ├── urls.py                      # Routes propres à l'app "stock"
│   └── views.py                      # ViewSets (logique métier des endpoints)
│
├── db.sqlite3               # Base de données SQLite (dev uniquement)
├── manage.py                 # Utilitaire CLI Django
└── readme.md                  # Ce fichier


2. Modèles (stock/models.py)

Warehouse (Entrepôt)

ChampTypeDescriptionnomCharFieldNom de l'entrepôtlocalisationCharFieldLocalisation physique (ville, zone...)capaciteIntegerFieldCapacité maximale de stockage (en unités)

Relation inverse : un entrepôt peut avoir plusieurs produits, accessibles via warehouse.produits.all() grâce au related_name='produits' défini sur Product.entrepot.

Product (Produit)

ChampTypeDescriptionnomCharFieldNom du produitquantitePositiveIntegerFieldQuantité en stock (ne peut pas être négative)etatCharField + choicesÉtat du produit : disponible, reserver, perimerdate_expirationDateFieldDate de péremption du produitentrepotForeignKey(Warehouse)Entrepôt auquel le produit est rattaché. on_delete=PROTECT : empêche la suppression d'un entrepôt tant qu'il contient des produits

Choix ETAT :

pythonETAT = [
    ('disponible', 'Disponible'),
    ('reserver', 'Reserver'),
    ('perimer', 'Perimer')
]


Remarque orthographe : les valeurs reserver et perimer sont utilisées comme clés techniques dans toute la base et l'API. Elles peuvent rester ainsi (ce sont des identifiants internes, pas du texte affiché), tant que le libellé humain (Reserver, Perimer) est correct côté frontend si besoin. Si tu préfères corriger, il faudra créer une migration de données pour les enregistrements déjà en base.




3. Endpoints API (stock/views.py)

Le projet utilise des ViewSets DRF enregistrés via un DefaultRouter (dans stock/urls.py / config/urls.py), ce qui génère automatiquement les routes CRUD standards, en plus des actions personnalisées ci-dessous.

ProductViewset

MéthodeURLDescriptionGET/products/Liste tous les produitsPOST/products/Crée un produitGET/products/{id}/Détail d'un produitPUT/PATCH/products/{id}/Modifie un produitDELETE/products/{id}/Supprime un produitPOST/products/{id}/move/Action personnalisée : déplace le produit vers un autre entrepôt

Action move — logique :


Récupère le produit ciblé (self.get_object()).
Lit newwarehouse_id dans le corps de la requête (request.data).
Renvoie une erreur 400 si newwarehouse_id est absent.
Renvoie une erreur 400 si le produit est déjà perimer (règle métier : un produit périmé ne peut pas être déplacé).
Récupère l'entrepôt cible avec get_object_or_404.
Réassigne product.entrepot et sauvegarde.


Requête exemple :

httpPOST /products/3/move/
Content-Type: application/json

{
  "newwarehouse_id": 2
}


⚠️ Bug corrigé dans cette version : la ligne originale

pythonnewwarehouse = get_object_or_404(Warehouse, newwarehouse_id)

passait newwarehouse_id comme argument positionnel, ce qui est invalide pour get_object_or_404 (il attend soit un filtre nommé, soit un dict). La correction :

pythonnewwarehouse = get_object_or_404(Warehouse, pk=newwarehouse_id)



WarehouseViewset

MéthodeURLDescriptionGET/warehouses/Liste tous les entrepôtsPOST/warehouses/Crée un entrepôtGET/warehouses/{id}/Détail d'un entrepôtPUT/PATCH/warehouses/{id}/Modifie un entrepôtDELETE/warehouses/{id}/Supprime un entrepôt (bloqué si des produits y sont rattachés — voir PROTECT)GET/warehouses/{id}/audit/Action personnalisée : renvoie le nombre total de produits de l'entrepôt

Action audit — logique :


Récupère l'entrepôt ciblé.
Compte ses produits liés via warehouse.produits.count().
Renvoie {"totalproduit": <nombre>}.


Réponse exemple :

json{
  "totalproduit": 42
}


 Piste d'amélioration possible : enrichir audit avec le détail par état (disponible, reserver, perimer) et le taux de remplissage (totalproduit / capacite * 100), utile pour un futur dashboard.




4. Permissions

Les deux ViewSets utilisent :

pythonpermission_classes = [IsAuthenticatedOrReadOnly]


Lecture (GET) : accessible à tout le monde, authentifié ou non.
Écriture (POST, PUT, PATCH, DELETE) : réservée aux utilisateurs authentifiés.



5. Installation et lancement

Prérequis


Python 3.10+
pip


Étapes

bash# 1. Cloner le projet
git clone <url-du-repo>
cd ECO_STOCK_DRF

# 2. Créer et activer un environnement virtuel
python -m venv venv
source venv/bin/activate      # Linux / Mac
venv\Scripts\activate         # Windows

# 3. Installer les dépendances
pip install django djangorestframework

# 4. Appliquer les migrations
python manage.py makemigrations
python manage.py migrate

# 5. Créer un super-utilisateur (accès admin)
python manage.py createsuperuser

# 6. Lancer le serveur
python manage.py runserver

L'API est ensuite disponible sur : http://127.0.0.1:8000/
L'admin Django (si les modèles y sont enregistrés) : http://127.0.0.1:8000/admin/


6. Tests

bashpython manage.py test

Fichier concerné : stock/tests.py. À compléter avec des cas couvrant notamment :


move : produit périmé → doit échouer.
move : newwarehouse_id manquant → doit échouer.
move : cas nominal → doit réussir et mettre à jour entrepot.
audit : comptage correct du nombre de produits.



7. Prochaines étapes possibles


Ajouter un modèle MouvementLog pour historiser chaque déplacement de produit (qui, quand, de quel entrepôt vers quel entrepôt).
Ajouter une validation empêchant de dépasser la capacite d'un entrepôt lors d'un move.
Ajouter la pagination sur les listes (/products/, /warehouses/).
Documenter l'API avec drf-spectacular ou drf-yasg (Swagger / OpenAPI).