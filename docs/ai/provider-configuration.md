# Configuration des fournisseurs IA

VISION INFINIE utilise le fournisseur local par défaut. Pour sélectionner explicitement un fournisseur compatible avec l’API OpenAI, définir les variables d’environnement suivantes dans le terminal ou dans le gestionnaire de secrets de l’environnement d’exécution :

    VISION_INFINIE_PROVIDER=openai-compatible
    VISION_INFINIE_BASE_URL=https://api.example.com/v1
    VISION_INFINIE_MODEL=nom-du-modele
    VISION_INFINIE_API_KEY=...

L’URL et le nom du modèle dépendent du fournisseur choisi. La clé doit rester secrète : ne pas la mettre dans le code, le README, un commit ou un message. Sur GitHub Actions, utiliser les secrets du dépôt seulement lorsqu’un test d’intégration réel est nécessaire.

Pour revenir au mode hors ligne, définir VISION_INFINIE_PROVIDER=local.

Les tests automatisés simulent la réponse HTTP et vérifient la configuration, l’authentification, le décodage et les erreurs. Ils ne contactent aucun fournisseur et ne nécessitent aucune clé réelle. Un test réel nécessite un compte fournisseur, un endpoint valide, un modèle disponible et une clé autorisée.
