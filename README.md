# apiservershoptest2

API Server shop.

Service généré par **fastapi-forge** le 2026-09-27 à partir du schéma `public`.

## Déployer

Il suffit de Docker avec le plugin compose. L'image de l'API est construite sur la machine et se connecte à une **base PostgreSQL existante** : ce dépôt ne crée aucune base.

```bash
git clone <url-de-ce-dépôt> apiservershoptest2 && cd apiservershoptest2
cp .env.example .env              # renseigner DATABASE_URL
docker compose up -d --build
curl localhost:8000/ready         # {"status":"ready"} : la base répond
```

La documentation interactive est sur http://localhost:8000/docs.

**La connexion (`DATABASE_URL`)** :

- **base sur un autre serveur** : `postgresql://utilisateur:motdepasse@serveur:5432/base` ;
- **base installée sur la même machine** : remplacer `localhost` par `host.docker.internal`. PostgreSQL doit alors accepter les connexions venant du réseau Docker (`listen_addresses` dans postgresql.conf, et une ligne pour `172.16.0.0/12` dans pg_hba.conf) ;
- **droits du compte** : `SELECT`, `INSERT`, `UPDATE`, `DELETE` sur les tables exposées et `USAGE` sur leurs séquences. Pour une API en lecture seule, `SELECT` suffit, mais les routes d'écriture répondront alors en erreur.

La base doit avoir la structure décrite par `db/schema.sql`, qui est la structure lue au moment de la génération. Si elle a changé depuis, régénérer le CRUD avec `forge sync`.

| Besoin | Commande |
|---|---|
| Mettre à jour | `git pull && docker compose up -d --build` |
| Afficher le commit sur `/health` | `GIT_SHA=$(git rev-parse --short HEAD) docker compose up -d --build` |
| État, logs | `docker compose ps` (healthy = base joignable), `docker compose logs -f api` |
| Arrêter | `docker compose down` |

## Organisation

| Dossier | Contenu | Qui écrit |
|---|---|---|
| `app/generated/` | modèles, schémas et routers CRUD | la forge, régénéré à chaque `forge sync` : ne pas modifier |
| `app/custom/routers/` | endpoints métier | l'IA (via `forge.yaml`) puis les devs ; jamais écrasé s'il a été modifié |
| `tests/generated/` | tests CRUD | la forge |
| `db/schema.sql` | snapshot du schéma : structure attendue de la base, utile aussi pour créer une base de test | la forge |
| `compose.yaml`, `.env.example` | déploiement : API construite sur place, connexion à la base par `DATABASE_URL` | la forge (une fois), puis vous |
| `forge.yaml` | configuration de la forge et description des endpoints métier | vous |
| `forge.lock.json` | traçabilité : hash du schéma, modèle IA, tentatives, empreinte du code | la forge |

## Développer en local

```bash
pip install -r requirements-dev.txt
export DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/base
uvicorn app.main:app --reload     # http://localhost:8000/docs
pytest -q
```

## Faire évoluer

```bash
# le schéma a changé -> régénère le CRUD, conserve le code métier
forge sync --db-url "$DATABASE_URL"          # ou : --schema-file schema.sql --scratch-db-url …

# nouvel endpoint métier : l'ajouter dans forge.yaml puis
forge sync --db-url "$DATABASE_URL"
```

## Endpoints

- `/categories` : CRUD sur `categories`
- `/customers` : CRUD sur `customers`
- `/orders` : CRUD sur `orders`
- `/products` : CRUD sur `products`
