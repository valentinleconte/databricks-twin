# databricks-twin — contexte projet

> Notes de travail entre sessions (comme sur openrag-twin). Pas destiné à un public externe —
> pour la doc publique, voir README.md une fois rédigé.

## Objectif

Réplique fonctionnelle sérieuse d'un produit agentique **Databricks**, pour un entretien lié à
Databricks — même démarche que `openrag-twin` (IBM/OpenRAG) : partir d'un vrai artefact officiel,
le faire tourner, le comprendre en profondeur, l'étendre avec un scénario à moi, prouver par la
mesure plutôt que par l'affirmation.

## Différence structurelle importante avec openrag-twin — à ne pas gommer

OpenRAG était un produit IBM **open-source, self-hostable, Apache 2.0** — on pouvait littéralement
cloner et faire tourner en local via Docker, sans compte IBM. Databricks est fondamentalement
différent : c'est une **plateforme SaaS**, pas un logiciel qu'on installe. Il n'existe pas
d'équivalent "clone et lance en Docker" — le narratif du README devra refléter ça honnêtement :
*"j'ai construit sur la vraie plateforme Databricks, avec leurs vrais outils, pas dans un
bac à sable isolé"* plutôt que *"j'ai forké leur produit"*.

## Prérequis — accès Databricks

- **Compte** : en cours d'inscription par l'utilisateur (Databricks Free Edition, Express Setup —
  gratuit, pas de carte bancaire, pas de compte cloud requis).
- **Recherché avant inscription** (voir conversation) : Free Edition inclut Unity Catalog +
  Vector Search (limité à 1 endpoint/1 unité) ; support de Model Serving/Foundation Model APIs
  et Mosaic AI Agent Framework **pas confirmé avec certitude** pour la Free Edition — à vérifier
  dès l'accès obtenu. Si trop limité, fallback sur l'essai 14 jours (Express Setup, sans carte,
  jusqu'à $400 de crédit, accès suspendu — pas facturé — si pas de moyen de paiement ajouté).
- **Piège identifié à éviter** : passer par un fournisseur cloud (AWS Marketplace etc.) plutôt
  que l'inscription directe Databricks peut entraîner une facturation séparée côté cloud,
  indépendante du crédit Databricks. Rester sur Express Setup.

## Le vrai "upstream" — trouvé et vérifié (pas juste supposé)

Contrairement à OpenRAG (un seul produit évident dès le départ), Databricks n'a pas un unique
repo officiel équivalent. Deux candidats identifiés :

- ❌ `databricks/genai-cookbook` — **déprécié** (message officiel de dépréciation dans le repo),
  à éviter. Aurait affaibli le narratif "produit réel, activement maintenu".
- ✅ **`databricks/app-templates`** — actif, mis à jour début août 2026. Contient ~40 templates
  (chatbots, agents, apps data). Cloné et inspecté directement (pas de résumé web) dans
  `agent-langgraph/` :
  - Agent LangGraph-style (`langchain_core.tools`, `create_agent`, `ChatDatabricks`), interface
    `ResponsesAgent` de MLflow.
  - Outils déjà commentés/prêts pour **Vector Search, Genie, UC functions, MCP servers** — pattern
    multi-outils directement exploitable pour notre scénario de routage (recherche doc vs ticket,
    comme OpenRAG).
  - `.claude/skills/` déjà présent dans le template (comme OpenRAG !) — bon signe de convention
    partagée dans l'écosystème.
  - `agent_server/evaluate_agent.py` : **évaluation MLflow native** avec scorers prêts à l'emploi
    (`ToolCallCorrectness`, `RelevanceToQuery`, `Safety`, `Completeness`, `ConversationalSafety`,
    `UserFrustration`...) + `ConversationSimulator` (simulation de conversation par persona).
    Potentiellement plus impressionnant que notre golden set fait main — à utiliser plutôt qu'à
    réinventer, ça prouve une vraie maîtrise MLflow (produit phare Databricks).
  - `uv run quickstart` / `uv run start-app` — tooling cohérent avec ce qu'on utilise déjà.

**Décision provisoire** : partir de `agent-langgraph` comme base, à confirmer une fois l'accès
workspace obtenu (vérifier que Vector Search + Model Serving sont bien utilisables en Free Edition).

## Licence — attention, différent d'Apache 2.0

`databricks/app-templates` est sous une **licence Databricks propriétaire** (pas Apache 2.0, pas
MIT). Lue en entier, points clés :
- Usage autorisé **seulement en connexion avec les Databricks Services** (pas un usage libre
  indépendant comme Apache 2.0) — devrait poser problème vu qu'on va justement l'utiliser avec un
  vrai compte Databricks actif.
- **Redistribution autorisée**, à condition de : inclure une copie de la licence, marquer les
  fichiers modifiés, conserver les mentions de copyright/attribution, inclure le contenu du
  fichier NOTICE dans toute œuvre dérivée qu'on distribue.
- **Résiliation** : la licence s'éteint automatiquement si l'accord Databricks prend fin — il
  faudrait alors supprimer les Licensed Materials. Point différent d'Apache 2.0 (où le code reste
  utilisable indéfiniment, sans lien avec un compte actif). À mentionner honnêtement dans le
  README, comme on l'a fait pour la licence Apache 2.0 d'OpenRAG.

## Accès workspace — vérifié en direct (CLI, pas supposé)

Authentifié via `databricks auth login` (OAuth navigateur, profil `databricks-twin` dans
`~/.databrickscfg`). Host : `dbc-1c1fb98c-23cd.cloud.databricks.com`.

- ✅ **Model Serving** : pleinement dispo, sans rien configurer. Endpoints Foundation Model déjà
  `READY` : chat (Llama 3.3 70B, Llama 4 Maverick, GPT OSS 120B/20B, Qwen3-Next-80B, Qwen3.5-122B,
  Gemma 3 12B, Llama 3.1 8B) + embeddings (GTE Large, BGE Large, Qwen3 Embedding 0.6B). Pas de
  Claude dans ce roster pay-per-token par défaut — à garder en tête pour le choix du LLM.
- ✅ **Vector Search** : confirmé en créant un vrai endpoint de test (`databricks-twin-test`,
  type STANDARD) — passé `ONLINE` immédiatement (serverless), puis supprimé après vérification.
- ✅ **Unity Catalog** : confirmé (`databricks catalogs list` → `workspace`, `system`, `samples`).

**Conclusion : la Free Edition suffit largement, pas besoin de l'essai 14 jours.** Les trois
briques nécessaires pour répliquer l'équivalent Databricks d'OpenRAG sont opérationnelles, à coût
zéro (pas de carte bancaire ajoutée).

## Template copié — attribution

Contenu de `databricks/app-templates/agent-langgraph` (commit HEAD au moment du clone, 25/08/2026)
copié dans la racine du repo — pas de `git clone` du monorepo entier (`app-templates` est une
collection de ~40 starter-kits, pas "le produit", donc pas de sens à en préserver l'historique
git complet). `LICENSE` et `NOTICE` copiés à la racine, inchangés, conformément aux obligations de
redistribution de la licence Databricks (voir section plus haut). Rien n'est encore modifié par
rapport au template d'origine — prochaine étape : personnaliser.

Petit conflit de nommage résolu : le template a son propre `CLAUDE.md` (juste un pointeur
`@AGENTS.md`, mécanisme d'import Claude Code — gardé tel quel, fonctionnel). Mes propres notes de
travail ont été déplacées ici, dans `NOTES.md`.

Source exacte : https://github.com/databricks/app-templates/tree/main/agent-langgraph

**Erreur évitée de justesse** : en créant le squelette de notre propre `README.md` (public,
esprit openrag-twin), j'ai écrasé sans le lire d'abord le `README.md` original du template
(314 lignes — setup, doc des fonctionnalités). Récupéré depuis `git show HEAD:README.md`
avant que ce soit commité, sauvegardé dans `docs/AGENT_TEMPLATE_README.md`. Rien perdu, mais
ça aurait dû être lu/renommé *avant* d'écrire dessus, pas après coup — leçon pour la suite.

## Premier bug rencontré & corrigé — même famille que les bugs OpenRAG

**Symptôme** : `uv run start-app` + première question dans le chat → `404 ENDPOINT_NOT_FOUND`
("The given endpoint does not exist").

**Cause racine** : `agent_server/agent.py` référence en dur `ChatDatabricks(endpoint="databricks-gpt-5-2")`
— un endpoint qui n'existe simplement pas dans le roster réellement disponible sur ce workspace
(vérifié via `databricks serving-endpoints list` : Llama 3.x/4, GPT OSS, Qwen3, Gemma 3, pas de
`gpt-5-2`, pas de Claude). Même famille que le version-skew d'OpenRAG (bug #4/#5) : un artefact
de config qui suppose un environnement différent de celui réellement déployé — sauf qu'ici c'est
un nom de endpoint plutôt qu'une version de package.

**Fix** : remplacé par `databricks-meta-llama-3-3-70b-instruct` (Llama 3.3 70B Instruct) — présent
et `READY`, choix solide pour du tool-calling agentique.

**Point annexe rencontré en cours de route** : deux faux départs de `uv run start-app` (échec
"port already in use") parce que tuer les PID parents (`uv run`, wrapper zsh) ne tue pas les
processus enfants réellement liés aux ports (uvicorn :8000, vite :3100) — il faut `lsof -ti :PORT
| xargs kill -9` sur les vrais processus, pas sur le PID du wrapper.

**Vérifié bout en bout** : `get_current_time` (l'outil d'exemple du template) appelé et exécuté
avec succès dans l'UI, réponse correcte affichée.

## Prochaines étapes

1. [x] ~~Attendre confirmation accès workspace~~ — fait, vérifié en CLI
2. [x] ~~Vérifier Vector Search / Model Serving~~ — les deux confirmés fonctionnels
3. [x] ~~Cloner `agent-langgraph` comme base réelle du projet~~ — fait
4. [x] ~~Choisir le LLM~~ — `databricks-meta-llama-3-3-70b-instruct` (voir bug ci-dessus)
5. [x] ~~Définir le scénario fonctionnel (routage)~~ — même scénario qu'OpenRAG (RAG doc vs second
   outil), mais le second outil est réimplémenté nativement Databricks : **Genie space** (NL-to-SQL)
   sur une table de tickets, au lieu du mock Python porté tel quel. Décision utilisateur confirmée.
6. [ ] README avec la licence Databricks correctement citée + NOTICE inclus

## Scénario fonctionnel — construction en cours

**Nom de l'app** : `agent-databricks-twin`. **Mémoire** : stateless (pas de Lakebase) — décision
utilisateur confirmée, cohérent avec le choix "pas de Postgres à opérer" pour ce projet démo.

**Corpus documentaire** (même trick auto-référentiel qu'OpenRAG — la doc des briques qui font
tourner le RAG lui-même) : 11 pages doc Databricks (`scripts/twin/fetch_databricks_docs.py`),
découpées en **196 chunks** (1000 car., overlap 200 — même paramétrage qu'OpenRAG) et chargées dans
`workspace.databricks_twin.doc_chunks` (Delta, `enableChangeDataFeed=true`, requis pour Vector
Search). Vérifié par `SELECT COUNT(*)` → 196, correspond au compte du chunker.

**Table structurée** `workspace.databricks_twin.support_tickets` — 8 tickets mock, mêmes IDs
101/102/103 qu'OpenRAG pour la continuité (même histoire, statut/priority/assignee/summary/updated),
+ 5 tickets supplémentaires (104-108) pour que le Genie space ait de quoi faire du vrai NL-to-SQL
(compter, filtrer, grouper) plutôt qu'un lookup à un seul enregistrement. Les résumés de tickets
104-108 sont volontairement écrits comme des clins d'œil aux vrais bugs de ce projet (endpoint
`databricks-gpt-5-2`, CDF manquant, permission Genie manquante...).

**Vector Search** :
- Endpoint `databricks-twin-vs` (type STANDARD) créé et `ONLINE`.
- Index `workspace.databricks_twin.doc_chunks_index` créé (`DELTA_SYNC`, `TRIGGERED`, embeddings
  managés via `databricks-gte-large-en` sur la colonne `content`). Provisioning initial en cours au
  moment de la rédaction (peut prendre plusieurs minutes la première fois sur un endpoint neuf) —
  à vérifier `status.ready == true` avant de tester l'agent en local.

**Genie Space** — **création UI-only, ne peut pas être automatisée en CLI** (confirmé : pas de
`databricks genie create-space`). Instructions données à l'utilisateur (voir message de session) :
créer un space sur `workspace.databricks_twin.support_tickets`, warehouse par défaut = "Serverless
Starter Warehouse" (`1f75e75518a91b9a`), le partager en `CAN_RUN` avec le service principal de
l'app (`databricks apps get agent-databricks-twin --output json --profile databricks-twin | jq -r
'.service_principal_name'`), puis me redonner le `space_id` (visible dans l'URL `.../genie/rooms/<id>`
ou via `databricks genie list-spaces`).

**Agent (`agent_server/agent.py`)** — réécrit pour utiliser les deux MCP servers Databricks-hébergés
au lieu de l'outil d'exemple `get_current_time` (supprimé) :
- `doc-search` → `{host}/api/2.0/mcp/vector-search/workspace/databricks_twin/doc_chunks_index`
- `support-tickets-genie` → `{host}/api/2.0/mcp/genie/{GENIE_SPACE_ID}` (ajouté seulement si
  `GENIE_SPACE_ID` est défini dans l'environnement — dégradation propre en attendant que
  l'utilisateur crée le space, pas de crash).
- Prompt de routage (`AGENT_INSTRUCTIONS`) prépendé aux messages en tant que message `system` —
  **pas** un paramètre `prompt=`/`instructions=` de `create_agent()` (ce template ne l'accepte pas,
  documenté dans `.claude/skills/modify-agent/SKILL.md`) : même leçon que l'appel d'API à respecter
  à la lettre plutôt que supposer une signature.

**`databricks.yml`** — ajouté `doc_search_index` (`uc_securable` sur l'index Vector Search,
permission `SELECT`) ; entrée `support_tickets_genie` laissée en commentaire, à activer une fois le
`space_id` connu. **Bug annexe corrigé au passage** : le target `prod` réécrasait le nom de l'app à
`agent-langgraph` (résidu du template, incohérent avec le nom choisi `agent-databricks-twin`) —
corrigé. `databricks bundle validate` → OK.
