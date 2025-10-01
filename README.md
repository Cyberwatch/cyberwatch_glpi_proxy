# cyberwatch_glpi_proxy

## Intégration de GLPI à Cyberwatch avec un micro-proxy Flask

Cette documentation décrit les étapes nécessaires pour intégrer GLPI à Cyberwatch en utilisant un micro-proxy basé sur Flask.

---

## Prérequis
- Une instance GLPI configurée
- Une instance Cyberwatch
- Accès à la machine avec Cyberwatch pour exécuter le micro-proxy

---

## 1. Configuration de l'API de GLPI avec une authentification

### A) Activation de l'API REST de GLPI

1. Accéder à l'onglet **API** dans **Configuration > Générale**.
2. Activer l'option **Activer l'API Rest**.
3. Activer l'option **Activer la connexion avec un jeton externe** pour l'authentification.

### B) Ajouter un client de l'API pour Cyberwatch

1. Dans la même page, cliquer sur **Ajouter un client de l'API**.
2. Ajouter un client API pour Cyberwatch.
3. Activer ce client.
4. Régénérer un **app_token** et le conserver.

### C) Générer un `user_token`

1. Avec l'utilisateur actuel ou un utilisateur **cyberwatch** créé dans GLPI pour l'API, régénérer un jeton API dans les préférences utilisateur.
2. Conserver le **user_token**.

---

## 2. Lancer un "micro-proxy" pour GLPI sur la machine Cyberwatch

### A) Installer les dépendances

Sur la machine Cyberwatch, installer les dépendances avec `pip3` en tant qu'utilisateur dédié (ex: `cyberwatch`) :

```bash
su - cyberwatch
pip3 install --user Flask Flask-BasicAuth
```

### B) Lancer le micro-proxy Flask

1. Modifier le fichier `data.json` avec les **User Token** et **App Token** configurés dans GLPI.

2. Lancer le micro-proxy sur le port 5000 :

```bash
export FLASK_APP=micro_proxy.py
python3 -m flask run --host=0.0.0.0 --port=5000
```

**Remarque :** Il est possible d'utiliser d'autres méthodes (systemctl...) pour démarrer Flask et assurer son redémarrage automatique après un reboot.

---

## 3. Mettre en place et tester une intégration avec GLPI

### A) Configuration de l'intégration

1. Accéder à **Administration > Intégration**.
2. Ajouter une nouvelle intégration en suivant les paramètres ci-dessous.

#### Modèle d'intégration

Personalisée

#### Protocole de l'intégration

Intégration HTTP

#### Emplacement du déclencheur
Choisir "Détails d'un actif - Onglet Gestion des correctifs"

#### URL

Mettre pour l'URL, l'IP de la machine et le port 5000 : http://[IP]:5000/glpi

#### En-têtes de la requête :

```json
{
  "Content-Type": "application/json",
  "Authorization": "Basic am9objptYXRyaXg="
}
```

> **Note** : Modifier "Authorization" selon la configuration `basic_auth` dans le script `micro_proxy.py`.

#### Corps de la requête :

```json
{
  "input": {
    "name": "[Cyberwatch] Actif {{ asset.name }} vulnérable",
    "content": "Bonjour,\n\n L’actif {{ asset.name }} est affecté par les vulnérabilités suivantes :\n\n{% for technology in technologies %}- {{ technology.product | escape }} - Version cible : {{ technology.target_version_string | default: 'Dernière version' | escape }}\n\n{{ cves | map: 'code' | join: ', ' }}\n\n{% endfor %}Merci de bien vouloir procéder à leur correction.",
    "status": "1",
    "urgency": "1"
  }
}
```

#### Méthode HTTP

Choisir "POST"

### B) Tester l'intégration

1. Dans l'inventaire, accéder aux détails d'une machine et sélectionner une CVE.
2. Tester l'intégration en envoyant une requête.
3. Vérifier que le ticket a bien été créé dans GLPI.
