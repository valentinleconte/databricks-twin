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

## Prochaines étapes

1. [x] ~~Attendre confirmation accès workspace~~ — fait, vérifié en CLI
2. [x] ~~Vérifier Vector Search / Model Serving~~ — les deux confirmés fonctionnels
3. [ ] Cloner `agent-langgraph` comme base réelle du projet (remplacer ce clone de review)
4. [ ] Choisir le LLM (pas de Claude en pay-per-token natif — voir si accessible autrement, ou
   choisir parmi le roster Llama/Qwen/GPT-OSS disponible)
5. [ ] Définir le scénario fonctionnel (routage) — à faire choisir par l'utilisateur, pas moi,
   même principe que pour OpenRAG
6. [ ] README avec la licence Databricks correctement citée + NOTICE inclus
