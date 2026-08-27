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
6. [x] ~~README avec la licence Databricks correctement citée + NOTICE inclus~~ — fait, README
   § License, NOTICE conservé intact à la racine
7. [x] ~~Déploiement réel + audit repo (CI, tests, topics, vidéo pitch)~~ — fait, voir sections
   "Déploiement réel" et suivantes ci-dessus
7. [x] ~~Éval (golden set + MLflow natif allégé)~~ — fait, 3 bugs réels trouvés et documentés
   (voir section "Évaluation" ci-dessous)

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
`databricks genie create-space`). Créé par l'utilisateur : "Support Ticket Management"
(`space_id=01f1a032e846136bb82ee33eb3e6a582`), warehouse "Serverless Starter Warehouse". Partage
avec le service principal de l'app **reporté après le déploiement** — l'app n'existe pas encore
(`databricks apps get agent-databricks-twin` → 404 tant que `bundle deploy` n'a pas tourné), donc
pas de service principal à partager pour l'instant ; en local on requête avec sa propre identité.

## Scénario vérifié bout en bout (local, `uv run start-app`, `:8000`/`:3100`)

Les 4 cas de routage testés en direct sur `/invocations` :
1. **Question doc seule** ("How does Vector Search sync with its source Delta table?") → tool
   `doc-search` appelé, réponse correcte, `source_url` cité exactement.
2. **Question ticket seule** ("status of ticket 104?") → tool Genie appelé, SQL généré par Genie
   correct (`SELECT status, assignee FROM ... WHERE ticket_id = '104'`), réponse exacte
   ("Open" / "Alice Martin").
3. **Question mixte** ("how many tickets Open, and what is Unity Catalog for?") → **les deux tools
   appelés dans la même requête**, compte exact (3 — tickets 101/104/105), réponse doc correcte
   avec 3 citations distinctes.
4. **Ticket inexistant** ("status of ticket 999?") → Genie répond "not found" côté SQL (aucune ligne),
   agent le restitue sans halluciner un statut.

**Bug trouvé et corrigé en cours de route** : au premier test du cas 1, la citation finale
contenait `.html` en suffixe du `source_url` (`.../vector-search.html`) — halluciné par le modèle,
alors que le `source_url` réellement retourné par le tool n'a pas ce suffixe. Cause : la consigne de
citation ("cite the source_url") n'imposait pas explicitement une copie verbatim. Fix : instruction
renforcée dans `AGENT_INSTRUCTIONS` ("copy it verbatim from the tool result, character for
character; never append, guess, or 'complete' a URL"). Retesté après fix → citation exacte, sans
suffixe inventé. Même famille de vigilance que les bugs OpenRAG : ne jamais supposer qu'un modèle
restitue un identifiant technique fidèlement sans le lui dire explicitement.

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

## Évaluation — décision et résultats

**Décision** (arbitrage utilisateur après présentation des deux options) : le golden set porté
d'openrag-twin (`eval/golden_set.yaml` + `eval/run_eval.py`) comme éval **principale** — rapide, peu
coûteuse (1 appel LLM/question), cohérence directe avec le travail déjà validé par un SE sur
openrag-twin. En complément, une version **allégée** de l'éval MLflow native
(`agent_server/evaluate_agent.py`) — 2 scorers ciblés (`RelevanceToQuery`, `ToolCallCorrectness`) sur
le même golden set, **sans** `ConversationSimulator` ni les 9 scorers du template (le fichier
d'origine faisait tourner une simulation multi-tours par persona + 9 juges LLM sur des cas
placeholder — cuisine vietnamienne, nombres de Fibonacci — sans rapport avec notre scénario, et
`user_model="databricks:/databricks-claude-sonnet-4-5"` qui n'existe pas sur ce workspace, même
famille de bug que `databricks-gpt-5-2`). Objectif assumé : prouver la maîtrise de l'outil MLflow
natif sans s'engager sur son coût plein — décision cohérente avec l'arbitrage Sonnet-vs-Opus déjà
pris sur openrag-twin.

**Golden set** (`eval/golden_set.yaml`) : 15 cas — 8 connaissance, 3 ticket connu, 1 ticket inconnu,
1 mixte, 1 hors-sujet, 1 hors-corpus — vérité terrain vérifiée à la main contre le corpus réel
(`databricks-docs-md/`) et la vraie table `support_tickets`. Scoring par regex/substring sur la
réponse réelle de `/invocations`, port direct du script openrag-twin (voir `eval/run_eval.py`) adapté
au format Responses API (pas de markdown `[source](...)`, citations en `Source URL: https://...`)
et à l'absence d'auth locale (pas de clé API app, on requête directement `:8000/invocations`).

**Résultat mesuré** (3 runs complets, `--runs 3 --allow-flaky`, résultats bruts dans
`eval/last_results.json`) :

```
TOTAL over 3 runs: 13/15, 11/15, 13/15  (mean 82%, min 73%, max 87%)
Stability: 10/15 cases passed all 3 runs.
```

Deux itérations sur le golden set lui-même avant ce résultat final : `ticket-02` et `mixed-01`
échouaient d'abord à cause de mes propres questions de test, pas de l'agent (`ticket-02` ne
demandait pas explicitement l'assignee alors que je l'exigeais en `expected_keywords` ; `mixed-01`
pareil sur le champ ticket). Corrigé en alignant la formulation sur `ticket-01` (qui, elle,
demandait bien les deux champs). **Volontairement documenté ici plutôt que caché** : un golden set
mal formulé qui semble "détecter un bug agent" alors que c'est le test qui est mal écrit est un
piège classique, pas différent en substance des bugs #4/#5 d'OpenRAG (config qui suppose un contexte
qui n'est pas le bon).

### Bug trouvé — fiabilité du tool-calling de Llama 3.3 70B Instruct (non corrigé, documenté)

- **Symptôme** : sur ~10-20% des appels d'outil individuels (premier appel ou second appel dans le
  même tour, peu importe), le modèle ne produit pas d'appel d'outil structuré mais recrache
  littéralement la syntaxe d'appel en texte brut dans le message final, par ex. :
  `<function=workspace__databricks_twin__doc_chunks_index>{"query": "Lakebase database type)}</function>`
  — remarquer le JSON malformé (parenthèse fermante en trop avant le `}`). Le tool n'est jamais
  réellement exécuté ; l'agent répond avec ce texte au lieu d'une réponse informative. Reproduit à
  l'identique en interrogeant `/invocations` en direct (pas un artefact du script d'éval) :
  même question posée 3 fois de suite en boucle → échoue 1 fois, réussit 2 fois (`know-04`, testé
  isolément avant la mesure finale).
- **Cause probable** : le connecteur `ChatDatabricks` traduit les tool calls du modèle depuis le
  format de sortie natif de Llama 3.3 (qui utilise sa propre syntaxe `<function=...>` en interne,
  documentée dans le chat template officiel de Meta) vers le format structuré attendu par
  LangChain/l'API Responses. Dans une fraction des générations, le modèle produit cette syntaxe avec
  un JSON légèrement malformé (guillemet ou parenthèse en trop) et le parseur échoue silencieusement
  à la reconnaître comme un appel d'outil — elle retombe alors comme texte de message normal. Pas
  investigué plus loin côté `databricks-langchain` (boîte fermée depuis l'agent) ; hypothèse
  raisonnable mais pas prouvée au niveau du code du connecteur.
- **Cas le plus exposé** : `mixed-01` (question qui nécessite d'appeler les deux outils dans le même
  tour) — **échoue 5 fois sur 5** sur l'ensemble des runs effectués (2 lors de la mesure de
  stabilité initiale + 3 lors de la mesure finale), toujours sur le second appel (recherche
  documentaire, après un premier appel Genie réussi). Cohérent avec l'hypothèse : plus un tour
  contient d'appels d'outils, plus la probabilité cumulée qu'au moins un échoue est élevée.
- **Décision : non corrigé, documenté et mesuré plutôt que masqué.** Options envisagées et écartées
  pour cette itération : changer de modèle (testerait une hypothèse différente sans la confirmer —
  décision reportée, voir message de session), ajouter une logique de retry côté agent (ajouterait
  de la complexité pour contourner une limitation du modèle plutôt que la comprendre). Le choix
  assumé ici est le même esprit que le changement Opus→Sonnet sur OpenRAG : mesurer honnêtement,
  documenter le compromis, ne pas prétendre que c'est parfait.

### Bug trouvé — hallucination hors-corpus occasionnelle (non corrigé, documenté)

- **Symptôme** : sur la question hors-corpus (`edge-02`, "how do I configure autoscaling for a
  Databricks all-purpose compute cluster?" — sujet réel mais absent des 11 pages ingérées), l'agent
  admet honnêtement l'absence d'info dans 4 des 6 exécutions observées ("the search results don't
  provide...") mais **invente une procédure complète et plausible** dans les 2 autres :
  > "1. Go to the Clusters page in the Databricks UI. 2. Click on the cluster you want to configure
  > autoscaling for. 3. Click..."
  Rien de ce contenu ne vient du tool `doc-search` — le modèle est retombé sur sa connaissance
  générale pré-entraînée de Databricks au lieu de rester strictement ancré sur ce que le RAG a
  retourné. Dans un cas intermédiaire, l'agent admet d'abord le manque ("don't directly answer...")
  puis enchaîne quand même sur "However, I can try to provide some general guidance" — un
  contournement explicite de sa propre admission.
- **Cause** : `AGENT_INSTRUCTIONS` demande de citer fidèlement les sources retournées mais n'interdit
  pas explicitement de répondre à partir de connaissances hors-tool quand la recherche ne retourne
  rien de pertinent. Contrairement au bug de citation (`.html` halluciné, corrigé plus haut), celui-ci
  touche au *contenu* de la réponse, pas juste à sa mise en forme — plus délicat à durcir sans risquer
  de rendre l'agent inutilement évasif sur des questions limites mais légitimes.
- **Décision : non corrigé, documenté.** Un vrai fix mériterait son propre cycle mesure/itération
  (resserrer le prompt, re-tester, vérifier que ça ne dégrade pas les cas `knowledge` qui passent) —
  hors scope de cette passe d'éval. Noté explicitement comme limitation connue plutôt que laissé
  implicite.

### MLflow natif (`agent_server/evaluate_agent.py`) — et un troisième bug trouvé au passage

Lancé sur le même golden set (15 questions, `RelevanceToQuery` + `ToolCallCorrectness`, jugement LLM
natif Databricks — pas de `model=` explicite, la plateforme résout son juge par défaut via
`MLFLOW_TRACKING_URI=databricks://...`).

**Bug trouvé — cache de token OAuth du CLI local sous charge concurrente.** Premier run
(`uv run agent-evaluate`) : **10/15 échecs** sur `relevance_to_query` **et** sur
`tool_call_correctness`, tous avec la même erreur : `default auth: databricks-cli: cannot get access
token: Error: forced token refresh: cache update: exit status 45`. Diagnostic : `evaluate()` lance
les scorers en parallèle sur les 15 lignes, chacun instanciant son propre client SDK qui relit/rafraîchit
le cache de token OAuth du CLI (`~/.databrickscfg`, backé par le trousseau macOS) — sous cette charge
concurrente, les lectures/écritures se télescopent et une fraction échoue. `databricks current-user
me` fonctionnait pourtant très bien en parallèle (auth CLI de base non affectée) : le problème est
spécifique à la contention créée par de nombreux clients SDK simultanés, pas à l'auth elle-même.
**Fix partiel testé** : `databricks auth token --profile databricks-twin` pour forcer un
rafraîchissement propre du cache juste avant de relancer → 2ᵉ run : **5/15 puis 4/15 échecs**
(nette amélioration, mais pas zéro — la contention concurrente reste possible même sur un cache
frais). **Décision : non éliminé, documenté.** Un vrai fix nécessiterait soit de sérialiser les
appels scorer (perd le bénéfice de parallélisation de `evaluate()`), soit d'investiguer le
comportement du cache CLI plus en profondeur (hors scope ici) — **et ce problème n'existerait
probablement pas en déploiement réel** : une app déployée s'authentifie via son service principal
(OAuth machine-to-machine), pas via le flux `databricks-cli` + trousseau local que ce script utilise
en dev. Distinction importante à savoir expliquer en entretien : ce bug est un artefact du
*tooling de dev local*, pas de l'architecture de l'agent lui-même.

**Résultat mesuré** (2ᵉ run, le plus propre, métriques réelles tirées du run MLflow
`a3977d8584854eada7c7debcb813206c`, calculées sur les lignes où le scorer a effectivement réussi à
juger — 10/15 pour l'une, 11/15 pour l'autre) :

```
relevance_to_query/mean       0.70
tool_call_correctness/mean    0.27
```

**Écart notable et non investigué plus loin** : `tool_call_correctness` (27%) est très en dessous du
taux de réussite mesuré par le golden set (82% de moyenne sur le routage). Deux méthodologies de
mesure différentes — un juge LLM avec ses propres critères vs. un scoring déterministe
regex/substring sur le contenu de la réponse — ne sont pas censées converger exactement, mais un tel
écart mérite d'être noté plutôt qu'ignoré : soit le juge `ToolCallCorrectness` est plus strict sur ce
qu'il considère un appel "raisonnable" (par ex. il pourrait pénaliser les cas où le tool-calling leak
de Llama produit un texte brut au lieu d'un vrai appel structuré — capturé par les traces MLflow que
le juge inspecte), soit autre chose. Pas creusé au niveau du détail des évaluations individuelles
(hors budget de cette passe) — signalé explicitement comme piste ouverte plutôt que laissé de côté
silencieusement.

Run MLflow consultable : https://dbc-1c1fb98c-23cd.cloud.databricks.com/ml/experiments/168280437378767/evaluation-runs?selectedRunUuid=a3977d8584854eada7c7debcb813206c

## Déploiement réel — `databricks bundle deploy` + `bundle run`

**Oubli corrigé avant de déployer** : 4 commits locaux (tout le câblage des outils + l'éval) n'avaient
jamais été poussés sur GitHub — je committais après chaque étape mais oubliais `git push`. Repéré
par l'utilisateur ("pq ya tjrs rien sur github ?"), corrigé immédiatement (`git push origin main`).
Rien de perdu, juste une négligence de process à surveiller la prochaine fois.

**Déploiement** : `databricks bundle deploy` (crée l'app, uploade 44 fichiers) puis
`databricks bundle run agent_langgraph` (démarre le compute, clone `e2e-chatbot-app-next`, installe,
build, démarre). App live : https://agent-databricks-twin-7474648390614555.aws.databricksapps.com
(`compute_status: ACTIVE`, `app_status: RUNNING`).

**Permission Genie déjà réglée par le bundle** : contrairement à ce qui était prévu (partage manuel
via l'UI, voir plus haut), la déclaration `genie_space` + `permission: CAN_RUN` dans `databricks.yml`
a suffi — `bundle deploy` l'a appliquée automatiquement au service principal de l'app
(`app-vi1pm8 agent-databricks-twin`). Vérifié via l'API permissions (`/api/2.0/permissions/genie/...`).

### Bug trouvé en prod — `CAN_RUN` sur le Genie space ne suffit pas, il faut aussi `SELECT` sur la table

- **Symptôme** : premier test de bout en bout sur l'app déployée (`POST .../invocations`,
  Bearer token OAuth CLI) → la question ticket échoue avec : *"the query was unable to retrieve the
  status and assignee of ticket 101 due to a permission error... no access to the
  'workspace.databricks_twin.support_tickets' table"*.
- **Cause racine** : `CAN_RUN` sur le Genie space autorise le service principal à *interroger* le
  space, mais Genie exécute ensuite le SQL généré **avec les propres droits UC du principal
  appelant** sur la table sous-jacente — un grant séparé, pas inclus dans le grant `genie_space` du
  bundle. En local ça fonctionnait parce que je requêtais avec mon propre compte utilisateur (déjà
  propriétaire de la table) ; en prod, le service principal de l'app n'a par défaut aucun droit UC.
- **Fix** : `GRANT USE CATALOG ON CATALOG workspace`, `GRANT USE SCHEMA ON SCHEMA
  workspace.databricks_twin`, et `GRANT SELECT ON TABLE workspace.databricks_twin.support_tickets`
  au service principal (`13a4dfdf-4b26-4005-99a2-e56464502264`, identifié par client_id). Retesté
  immédiatement après → ticket 101 correctement retourné ("Open" / "Alice Martin").
- **Leçon** : le grant déclaratif dans `databricks.yml` (`resources: - genie_space: ...`) ne couvre
  que l'accès au *space* lui-même, pas la chaîne de droits UC dont Genie a besoin en aval pour
  exécuter le SQL qu'il génère. À vérifier explicitement en prod, pas supposé équivalent au
  comportement observé en local avec un compte utilisateur déjà privilégié.

**Vérifié en production, les deux outils** (Bearer token OAuth CLI, `stream: true` requis — voir
`.claude/skills/deploy/SKILL.md`, un premier essai sans `stream` avait renvoyé un 502, probablement
un démarrage à froid plutôt qu'un vrai problème de format) :
- Ticket : "What is the status of ticket 101, and who is it assigned to?" → "Open" / "Alice Martin" ✓
- Doc : "What is a data lakehouse?" → réponse correcte + citation `https://docs.databricks.com/aws/en/lakehouse` ✓
  (retestée après un premier échec — le bug de fiabilité tool-calling de Llama 3.3 70B documenté
  plus haut se reproduit aussi en prod, cohérent avec l'hypothèse que c'est un problème du modèle,
  pas de l'environnement local)
