# 🏪 Système de Gestion de Stock - Documentation

## Vue d'ensemble

Ce système de gestion de stock est conçu pour gérer plusieurs boutiques avec un système d'authentification multi-niveau et une gestion complète des stocks, ventes et comptabilité.

## 🏗️ Architecture des Modèles

### 1. **Structure générale**

#### **Store (Boutique)**
- Représente une boutique/entreprise
- Chaque boutique est indépendante
- Un super admin peut accéder à toutes les boutiques

#### **User (Utilisateur)**
- **Super admin** : `store = null`, accès global via Django Admin
- **Utilisateur de boutique** : `store = boutique_id`, accès limité à sa boutique
- Contrainte unique : `username` unique par boutique

### 2. **Gestion des stocks**

#### **Warehouse (Magasin/Entrepôt)**
- Lieux physiques de stockage dans une boutique
- Une boutique peut avoir plusieurs magasins/entrepôts

#### **Product (Produit)**
- Identifié par une `reference` unique
- Lié à une boutique spécifique
- Suivi du stock minimum d'alerte

#### **ProductStock (Stock par Magasin)**
- Quantité disponible par produit et par magasin
- Mise à jour automatique lors des entrées/sorties

### 3. **Personnel**

#### **Employee (Employé)**
- Employés enregistrés sans accès connexion
- Suivi : nom, téléphone, poste, salaire, date d'embauche
- Utilisé pour la gestion RH et traçabilité

### 4. **Partenaires commerciaux**

#### **Supplier (Fournisseur)**
- Fournisseurs de la boutique
- Liés aux bons d'entrée

#### **Customer (Client)**
- Clients de la boutique
- Peuvent être enregistrés ou non lors des ventes

### 5. **Flux de stock**

#### **StockEntry (Bon d'Entrée)**
- Arrivage de marchandises
- Lié à un fournisseur et un magasin
- Génération automatique du numéro : `ENT-{store_id}-{number}`

#### **StockEntryItem (Article du Bon d'Entrée)**
- Détail des produits reçus
- Quantité et prix d'achat
- Mise à jour automatique du stock

#### **StockExit (Bon de Sortie)**
- Vente/sortie de marchandises
- Génération automatique du numéro : `SOR-{store_id}-{number}`

#### **StockExitItem (Article du Bon de Sortie)**
- Détail des produits vendus
- Quantité et prix de vente
- Réduction automatique du stock

### 6. **Facturation**

#### **Invoice (Facture)**
- Générée automatiquement pour chaque bon de sortie
- Numéro automatique : `FAC-{store_id}-{number}`
- Lien direct avec le bon de sortie

### 7. **Comptabilité**

#### **Account (Compte)**
- Comptes bancaires et caisses de la boutique
- Types : `bank` (Banque) ou `cash` (Caisse)
- Suivi automatique du solde

#### **FinancialTransaction (Transaction Financière)**
- Mouvements de fonds liés aux opérations
- Types :
  - `purchase` : Achat (paiement fournisseur)
  - `sale` : Vente (encaissement client)
  - `transfer` : Transfert entre comptes
  - `adjustment` : Ajustement
- Mise à jour automatique des soldes

## 🔄 Flux de Travail

### Processus d'Achat (Entrée Stock)
1. Création d'un **StockEntry** avec fournisseur et magasin
2. Ajout des **StockEntryItem** (produits, quantités, prix)
3. Mise à jour automatique du **ProductStock**
4. Création automatique d'une **FinancialTransaction** de type `purchase`
5. Réduction du solde du compte utilisé pour le paiement

### Processus de Vente (Sortie Stock)
1. Création d'un **StockExit** avec client (optionnel) et magasin
2. Ajout des **StockExitItem** (produits, quantités, prix)
3. Vérification et réduction automatique du **ProductStock**
4. Génération automatique d'une **Invoice**
5. Création automatique d'une **FinancialTransaction** de type `sale`
6. Augmentation du solde du compte d'encaissement

### Transfert entre Comptes
1. Création d'une **FinancialTransaction** de type `transfer`
2. Spécification du compte source (`from_account`) et destination (`to_account`)
3. Mise à jour automatique des soldes

## 🔧 Fonctionnalités Clés

### Génération Automatique de Numéros
- **Bons d'entrée** : `ENT-{store_id}-{number:05d}`
- **Bons de sortie** : `SOR-{store_id}-{number:05d}`
- **Factures** : `FAC-{store_id}-{number:05d}`
- **Transactions** : `TRX-{YYYYMMDD}-{number:04d}`

### Contrôle de Stock
- Vérification automatique de disponibilité avant vente
- Alertes sur stock minimum
- Traçabilité complète des mouvements

### Sécurité et Isolation
- Isolation complète des données par boutique
- Contraintes uniques appropriées
- Gestion des permissions par utilisateur

### Comptabilité Intégrée
- Liaison automatique entre opérations stock et mouvements financiers
- Suivi en temps réel des soldes
- Historique complet des transactions

## 📊 Rapports Disponibles

### Stock
- Stock actuel par magasin
- Mouvements de stock par période
- Produits en rupture ou proche du minimum

### Ventes
- Chiffre d'affaires par période
- Ventes par produit
- Performance par magasin

### Comptabilité
- Soldes des comptes
- Mouvements financiers
- Réconciliation ventes/encaissements

## 🚀 Utilisation

### Interface d'Administration Django
- Accès via `/admin/`
- Gestion complète de tous les modèles
- Interfaces optimisées avec filtres et recherche

### Super Admin
- Accès à toutes les boutiques
- Gestion des utilisateurs globaux
- Configuration système

### Utilisateur de Boutique
- Accès limité à sa boutique
- Gestion des stocks et ventes
- Consultation des rapports

## 📝 Notes Techniques

### Base de Données
- SQLite en développement
- Support PostgreSQL/MySQL en production
- Migrations Django automatiques

### Performance
- Index sur les champs fréquemment recherchés
- Contraintes d'intégrité au niveau base
- Optimisations des requêtes avec `select_related`

### Extensibilité
- Architecture modulaire
- Modèles extensibles
- Support multi-boutiques natif
