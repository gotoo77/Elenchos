# État de l'art — Elenchos

> **Question directrice : peut-on exploiter des relations structurées entre productions faillibles de LLM pour détecter, localiser, tolérer ou corriger certaines erreurs sans connaître la vérité à l'avance ?**

**Statut :** document de travail initial  
**Projet :** Elenchos  
**Langue :** français  
**Date :** août 2026

---

## 1. Objet de cet état de l'art

Elenchos part d'une intuition inspirée des codes détecteurs et correcteurs d'erreurs :

> lorsqu'on ne connaît pas directement la vérité, peut-on ajouter ou exploiter suffisamment de structure, de redondance ou de contraintes entre plusieurs représentations d'une même information pour rendre certaines erreurs détectables — voire corrigibles ?

Cette question se situe à l'intersection de plusieurs domaines déjà bien établis :

- raisonnement multi-échantillons des LLM ;
- auto-évaluation et autocorrection ;
- débat multi-agent ;
- vérification et test-time compute ;
- metamorphic testing et problème de l'oracle ;
- diversité logicielle et N-version programming ;
- tolérance aux fautes byzantines ;
- théorie des codes correcteurs ;
- calibration et estimation d'incertitude ;
- vérification déterministe et outils externes.

L'objectif n'est donc pas de prétendre qu'Elenchos crée un domaine ex nihilo.

L'objectif est de déterminer plus précisément :

1. ce qui existe déjà ;
2. ce qui ressemble seulement superficiellement à l'idée ;
3. quelles limites connues doivent être intégrées dès le départ ;
4. et s'il reste une question de recherche distincte autour d'un éventuel **analogue du syndrome d'erreur** pour les productions de LLM.

---

# 2. Le problème fondamental : l'oracle

Dans un test classique, déterminer qu'une réponse est fausse suppose généralement de connaître la bonne réponse.

On dispose alors d'un oracle :

```text
entrée x
   │
   ▼
 système
   │
   ▼
 réponse y
   │
   ▼
 comparer à y*
   │
   ▼
 correct / incorrect
```

Mais le cas intéressant pour Elenchos est précisément celui où `y*` n'est pas disponible.

```text
entrée x
   │
   ▼
 LLM
   │
   ▼
 réponse y

 y* = inconnue
```

Une partie importante de la littérature étudiée tente de contourner ce problème en remplaçant l'oracle direct par autre chose :

- consensus entre plusieurs générations ;
- auto-évaluation ;
- critique ;
- vérificateur appris ;
- outil externe ;
- relation métamorphique ;
- contrainte structurelle ;
- interaction entre agents ;
- redondance ou diversité des sources.

La question d'Elenchos est de savoir **quelles formes de structure apportent réellement de l'information nouvelle sur la correction d'une réponse**, et lesquelles ne font que répéter la même source d'erreur.

---

# 3. Self-consistency : la redondance par échantillonnage

## 3.1 Principe

Wang et al. proposent la **self-consistency** comme méthode de décodage pour le chain-of-thought.

Au lieu de produire un seul raisonnement, le modèle génère plusieurs trajectoires de raisonnement, puis la réponse finale la plus fréquente est sélectionnée.

Schématiquement :

```text
                ┌─ raisonnement A ── réponse 42
question ───────┼─ raisonnement B ── réponse 42
                ├─ raisonnement C ── réponse 37
                └─ raisonnement D ── réponse 42

                         ↓

                   réponse = 42
```

Les auteurs rapportent des gains importants sur plusieurs benchmarks de raisonnement.

### Référence

Xuezhi Wang et al., *Self-Consistency Improves Chain of Thought Reasoning in Language Models*, ICLR 2023.  
https://arxiv.org/abs/2203.11171

---

## 3.2 Rapport avec Elenchos

La self-consistency constitue une **baseline fondamentale**.

Elle exploite bien de la redondance.

Mais elle repose essentiellement sur :

> plusieurs trajectoires indépendantes devraient converger plus souvent vers la bonne réponse que vers une même mauvaise réponse.

Cela ressemble davantage à de la répétition probabiliste qu'à un véritable code correcteur.

La relation entre les échantillons est faible :

```text
A == B == D
```

et l'information principalement exploitée est la fréquence.

---

## 3.3 Limite majeure : erreurs corrélées

Le problème est que les erreurs des LLM ne sont pas nécessairement indépendantes.

Kim et al. ont étudié plus de 350 modèles et constatent une corrélation substantielle des erreurs. Sur l'un des benchmarks étudiés, lorsque deux modèles se trompent tous les deux, ils donnent la même erreur environ 60 % du temps.

### Référence

Elliot Myunghoon Kim et al., *Correlated Errors in Large Language Models*, ICML 2025.  
https://proceedings.mlr.press/v267/kim25e.html

Cela invalide une hypothèse naïve :

```text
plus de modèles
     ≠
plus d'évidence indépendante
```

On peut avoir :

```text
LLM A ──┐
LLM B ──┼── même biais / mêmes données / mêmes heuristiques
LLM C ──┘

                ↓

          même erreur
```

Pour Elenchos, **la diversité effective des canaux d'information** devra donc être mesurée ou au moins approximée.

---

# 4. Auto-évaluation et calibration

## 4.1 « Language Models (Mostly) Know What They Know »

Kadavath et al. étudient la capacité des modèles à estimer la validité de leurs propres réponses.

Ils observent notamment que de grands modèles peuvent produire des estimations de type `P(True)` raisonnablement calibrées dans certaines conditions, et que l'évaluation peut bénéficier de plusieurs échantillons.

### Référence

Saurav Kadavath et al., *Language Models (Mostly) Know What They Know*, 2022.  
https://arxiv.org/abs/2207.05221

---

## 4.2 Rapport avec Elenchos

Cette famille de travaux montre qu'une production LLM peut contenir **des signaux secondaires relatifs à sa propre fiabilité**.

Mais une probabilité auto-déclarée reste un canal produit par le même système.

```text
LLM
 ├── réponse
 └── confiance sur cette réponse
```

Si la réponse et la confiance partagent le même angle mort, la seconde n'apporte pas nécessairement une observation indépendante.

Elenchos devra distinguer :

- **redondance nominale** : plusieurs sorties ;
- **redondance informationnelle** : plusieurs sorties contenant effectivement des preuves indépendantes.

---

# 5. Self-Refine, Reflexion et autocorrection

## 5.1 Self-Refine

Self-Refine propose une boucle dans laquelle un modèle :

1. produit une réponse ;
2. critique cette réponse ;
3. la raffine ;
4. répète éventuellement le processus.

```text
réponse
   ↓
critique
   ↓
révision
   ↓
nouvelle critique
   ↓
...
```

### Référence

Aman Madaan et al., *Self-Refine: Iterative Refinement with Self-Feedback*, NeurIPS 2023.  
https://arxiv.org/abs/2303.17651

---

## 5.2 Reflexion

Reflexion ajoute une mémoire textuelle de l'échec et utilise des signaux de retour issus de l'environnement ou simulés pour améliorer les essais suivants.

### Référence

Noah Shinn et al., *Reflexion: Language Agents with Verbal Reinforcement Learning*, 2023.  
https://arxiv.org/abs/2303.11366

---

## 5.3 Les limites de l'autocorrection intrinsèque

La littérature est loin d'être unanime sur l'efficacité de l'autocorrection lorsqu'aucun signal externe fiable n'est disponible.

Kamoi et al. proposent en 2024 une revue critique de la littérature et soulignent que :

- les résultats dépendent fortement de la nature du feedback ;
- certaines évaluations peuvent surestimer l'autocorrection ;
- les résultats négatifs sont nombreux lorsque l'agent ne dispose d'aucune information externe supplémentaire.

### Référence

Ryo Kamoi et al., *When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of Self-Correction of LLMs*, TACL 2024.  
https://aclanthology.org/2024.tacl-1.78/

Des travaux plus récents confirment que l'autocorrection intrinsèque peut échouer en l'absence d'oracle ou de signal supplémentaire.

### Référence

Qingjie Zhang et al., *Understanding the Dark Side of LLMs' Intrinsic Self-Correction*, ACL 2025.  
https://aclanthology.org/2025.acl-long.1314/

Un résultat particulièrement intéressant publié en 2026 suggère par ailleurs que les modèles corrigent beaucoup plus facilement une erreur lorsqu'elle leur est présentée comme provenant d'une source externe que lorsqu'elle est présentée comme leur propre raisonnement.

### Référence

Kuan-Yen Chen et al., *The Self-Correction Illusion: LLMs Correct Others but Not Themselves*, 2026.  
https://arxiv.org/abs/2606.05976

---

## 5.4 Conséquence pour Elenchos

Ces résultats renforcent une intuition centrale :

> répéter un raisonnement ou demander au même agent de « réfléchir davantage » ne crée pas nécessairement une nouvelle source d'information.

Une architecture Elenchos devrait donc expliciter pour chaque vérification :

```text
Quelle nouvelle information est introduite ici ?
```

Si la réponse est :

```text
aucune, le même modèle regarde simplement sa propre sortie
```

alors l'étape est peut-être utile pragmatiquement, mais elle ne constitue pas une redondance forte au sens qui nous intéresse.

---

# 6. Chain-of-Verification

Chain-of-Verification (CoVe) est beaucoup plus proche de l'intuition d'Elenchos.

La méthode :

1. produit une réponse initiale ;
2. génère des questions de vérification ;
3. répond à ces questions indépendamment ;
4. utilise ces résultats pour produire une réponse finale.

```text
question
   │
   ▼
réponse initiale
   │
   ▼
questions de vérification
   │
   ├── V1
   ├── V2
   └── V3
       │
       ▼
réponse finale
```

L'indépendance des questions de vérification est explicitement utilisée pour réduire le biais lié à la réponse initiale.

### Référence

Shehzaad Dhuliawala et al., *Chain-of-Verification Reduces Hallucination in Large Language Models*, Findings of ACL 2024.  
https://arxiv.org/abs/2309.11495  
https://aclanthology.org/2024.findings-acl.212/

---

## Rapport avec Elenchos

CoVe est probablement l'un des ancêtres opérationnels les plus proches de ce que pourrait devenir un protocole élénctique.

Mais CoVe reste principalement une **stratégie de vérification procédurale**.

Elenchos cherche à poser une question plus générale :

> peut-on caractériser les relations entre plusieurs représentations ou observations de façon suffisamment explicite pour savoir **quelles classes d'erreurs ces relations permettent de détecter** ?

La différence serait analogue à :

```text
méthode empirique efficace
          vs
structure dont on caractérise les propriétés
```

---

# 7. Débat multi-agent

Du et al. proposent de faire débattre plusieurs instances de modèles pendant plusieurs tours avant d'agréger leur réponse.

### Référence

Yilun Du et al., *Improving Factuality and Reasoning in Language Models through Multiagent Debate*, 2023.  
https://arxiv.org/abs/2305.14325

Le mécanisme est intuitivement élénctique :

```text
Agent A : proposition
Agent B : objection
Agent A : réponse
Agent C : contradiction
...
```

Le débat peut exposer :

- contradictions ;
- erreurs de calcul ;
- hypothèses implicites ;
- arguments faibles.

---

## Limite

Le débat ne garantit pas que la bonne information existe dans le système.

Trois agents partageant le même angle mort peuvent construire ensemble une justification très cohérente d'une erreur.

```text
cohérence argumentative ≠ vérité
```

Le débat apporte potentiellement un **canal de recherche d'incohérences**, mais n'est pas à lui seul une garantie de correction.

---

# 8. Tolérance aux fautes byzantines

Le rapprochement avec les systèmes distribués est particulièrement important.

Dans le problème classique des généraux byzantins, certains participants peuvent transmettre des informations arbitrairement incorrectes ou contradictoires.

Le problème consiste à construire un protocole permettant aux participants honnêtes d'atteindre certaines propriétés de consensus malgré ces fautes.

### Référence historique

Leslie Lamport, Robert Shostak, Marshall Pease, *The Byzantine Generals Problem*, ACM TOPLAS, 1982.

Présentation synthétique :  
https://www.cs.cornell.edu/courses/cs614/1999sp/notes99/byzantine.html

---

## 8.1 Application récente aux systèmes multi-LLM

En 2026, Lee et al. étudient explicitement les réseaux multi-agents LLM en présence d'agents byzantins.

Ils proposent **Self-Anchored Consensus (SAC)**, où les agents échangent leurs réponses, filtrent localement les messages jugés peu fiables puis raffinent leur réponse.

Ils dérivent des conditions de robustesse du graphe de communication permettant de limiter l'influence byzantine.

### Référence

Haejoon Lee et al., *Robust Multi-Agent LLMs under Byzantine Faults*, 2026.  
https://arxiv.org/abs/2605.09076

---

## 8.2 Différence avec Elenchos

La tolérance byzantine répond principalement à :

> comment atteindre un résultat robuste lorsque certains participants sont arbitrairement fautifs ?

Elenchos s'intéresse plutôt à :

> que peut-on **inférer sur l'erreur elle-même** à partir des relations entre les informations disponibles ?

Les deux questions se recouvrent partiellement, mais ne sont pas identiques.

---

# 9. N-version programming et diversité logicielle

Le **N-version programming** utilise plusieurs implémentations indépendantes d'une même spécification.

```text
           ┌── implémentation A ── résultat A
entrée ────┼── implémentation B ── résultat B
           └── implémentation C ── résultat C
                         │
                         ▼
                     vote / arbitre
```

L'objectif est de tolérer les bugs d'une implémentation grâce à la diversité des autres.

### Référence de synthèse

John C. Knight, *N-Version Programming*, 2002.  
https://onlinelibrary.wiley.com/doi/abs/10.1002/0471028959.sof219

---

## Le problème classique : fautes communes

L'efficacité du N-version programming dépend fortement de l'indépendance des fautes.

Des implémentations différentes peuvent reproduire les mêmes erreurs lorsqu'elles résultent :

- d'une ambiguïté de spécification ;
- d'une même interprétation humaine ;
- d'un même algorithme ;
- de dépendances communes.

Cette question est directement analogue au problème des erreurs corrélées entre LLM.

---

# 10. Error-Correcting Output Codes en apprentissage automatique

Les **Error-Correcting Output Codes (ECOC)** utilisent explicitement des idées de théorie des codes pour transformer une classification multiclasse en plusieurs problèmes binaires.

Chaque classe reçoit un mot de code.

Exemple simplifié :

```text
classe A : 1 0 1 1 0
classe B : 0 1 1 0 1
classe C : 1 1 0 0 1
```

Plusieurs classifieurs produisent les bits du mot estimé, puis la classe correspondant au mot valide le plus proche est sélectionnée.

### Référence

Thomas G. Dietterich, Ghulum Bakiri, *Error-Correcting Output Codes: A General Method for Improving Multiclass Inductive Learning Programs*, 1991.

https://www.semanticscholar.org/paper/Error-Correcting-Output-Codes%3A-A-General-Method-for-Dietterich-Bakiri/2ce4103e5bc275498adc81c422777ea404b5e599

---

## Rapport avec Elenchos

ECOC montre qu'il existe déjà un précédent très concret pour appliquer des concepts de codes correcteurs à des systèmes d'apprentissage.

Mais la situation est beaucoup plus contrôlée :

- l'espace des classes est connu ;
- les mots de code sont construits explicitement ;
- une distance est définie ;
- le décodage est bien déterminé.

Dans le cas d'une réponse ouverte de LLM :

```text
« explique pourquoi cette proposition est vraie »
```

nous ne disposons pas naturellement :

- d'un alphabet fini ;
- d'un mot de code canonique ;
- d'une métrique de Hamming ;
- ni d'un décodeur.

C'est précisément l'un des sauts théoriques qu'Elenchos devrait examiner.

---

# 11. Metamorphic testing : le cousin conceptuel majeur

Le **metamorphic testing** a été conçu pour les situations où le résultat attendu d'un programme est difficile ou impossible à connaître directement.

Au lieu de tester :

```text
f(x) == résultat attendu
```

on teste une relation entre plusieurs exécutions.

Par exemple :

```text
si T transforme x d'une manière connue,
alors f(T(x)) doit entretenir une relation R avec f(x).
```

Formellement :

```text
R(x, T(x), f(x), f(T(x))) = vrai
```

L'oracle direct est remplacé par une **relation métamorphique**.

---

## 11.1 Exemple simple

Pour un tri :

```text
sort(x) = y
```

Même sans connaître `y` à l'avance, certaines relations doivent être vraies.

Par exemple :

```text
sort(sort(x)) == sort(x)
```

Si cette relation est violée, une erreur est détectée.

On ne connaît pas nécessairement le résultat attendu initial.

Mais on connaît une propriété qu'un résultat correct doit respecter.

---

## 11.2 Metamorphic testing appliqué aux LLM

Cho, Ruberto et Terragni ont publié en 2025 une étude particulièrement pertinente sur le metamorphic testing des LLM pour des tâches NLP.

Ils recensent **191 relations métamorphiques** dans la littérature et expérimentent un sous-ensemble de 36 relations, pour environ **560 000 tests métamorphiques**.

Leur motivation est explicitement le **problème de l'oracle** : détecter des comportements fautifs sans disposer nécessairement de jeux de données étiquetés.

### Référence

Steven Cho, Stefano Ruberto, Valerio Terragni, *Metamorphic Testing of Large Language Models for Natural Language Processing*, 2025.  
https://arxiv.org/abs/2511.02108

---

# 12. Pourquoi le metamorphic testing est particulièrement important pour Elenchos

C'est probablement le voisin conceptuel le plus proche de l'intuition initiale du projet.

Elenchos :

```text
je ne connais pas nécessairement la vérité
             │
             ▼
je construis plusieurs observations liées
             │
             ▼
je vérifie les relations entre elles
             │
             ▼
la violation constitue un signal d'erreur
```

Metamorphic testing :

```text
je ne connais pas nécessairement f(x)
             │
             ▼
je construis T(x)
             │
             ▼
je compare f(x) et f(T(x))
             │
             ▼
la violation de R constitue un signal d'erreur
```

La ressemblance est profonde.

Mais Elenchos pourrait chercher à généraliser cette idée au-delà des transformations d'entrée, vers une famille plus large de **contraintes redondantes sur des représentations sémantiques**.

---

# 13. Vers une « parité sémantique »

Considérons une proposition `P`.

On pourrait demander au système non pas seulement de produire `P`, mais plusieurs représentations liées :

```text
P  = réponse directe
Q  = conséquence logique supposée de P
R  = reformulation indépendante de P
S  = réponse au problème transformé
T  = résultat d'un outil déterministe partiel
```

Ces éléments peuvent définir des contraintes :

```text
C1(P, Q)
C2(P, R)
C3(Q, S)
C4(P, T)
```

Le système produit alors un vecteur de violations :

```text
s = [C1, C2, C3, C4]

exemple :

s = [0, 1, 0, 1]
```

où `1` signifie qu'une contrainte attendue est violée.

Ce vecteur ressemble structurellement à un **syndrome d'erreur** en théorie des codes.

Cela ne signifie pas encore qu'il en possède les propriétés mathématiques.

Mais c'est une piste de formalisation particulièrement intéressante.

---

# 14. Le syndrome en théorie des codes : ce que l'analogie exigerait réellement

Dans un code linéaire classique, un mot valide `c` satisfait :

```text
Hcᵀ = 0
```

où `H` est une matrice de contrôle de parité.

Si un mot reçu est :

```text
r = c + e
```

alors :

```text
Hrᵀ = H(c + e)ᵀ
     = Hcᵀ + Heᵀ
     = Heᵀ
```

Le résultat :

```text
s = Hrᵀ
```

est appelé **syndrome**.

Le point fondamental est remarquable :

> le syndrome contient une information sur l'erreur sans nécessiter de connaître le mot original transmis.

C'est exactement la propriété qui rend l'analogie séduisante pour Elenchos.

---

# 15. Ce qu'il faudrait pour qu'Elenchos mérite réellement l'analogie

Pour aller au-delà d'une métaphore, il faudrait progressivement définir des équivalents à :

| Théorie des codes | Candidat Elenchos |
|---|---|
| message | information / réponse recherchée |
| encodage | génération de représentations redondantes |
| bits de parité | contraintes / relations supplémentaires |
| canal bruité | LLM / processus de génération faillible |
| erreur | hallucination, contradiction, raisonnement incorrect |
| mot reçu | ensemble des productions |
| matrice de contrôle | ensemble de contraintes vérifiables |
| syndrome | motif de violations des contraintes |
| distance | notion de divergence entre représentations |
| décodage | sélection ou reconstruction d'une réponse |
| capacité de correction | classe d'erreurs dont la source peut être identifiée et réparée |

Aujourd'hui, la majorité de ces correspondances ne sont que des **hypothèses de travail**.

---

# 16. Verification et test-time compute

Une autre famille devenue majeure depuis 2024-2026 est celle du **test-time compute**.

L'idée générale consiste à consacrer davantage de calcul lors de l'inférence :

- produire plusieurs candidats ;
- explorer plusieurs trajectoires ;
- utiliser un vérificateur ;
- sélectionner ou raffiner les meilleures solutions.

Snell et al. montrent que l'allocation adaptative de calcul à l'inférence peut être très efficace sur des problèmes de raisonnement.

### Référence

Charlie Snell et al., *Scaling LLM Test-Time Compute Optimally Can Be More Effective than Scaling Parameters for Reasoning*, ICLR 2025.  
https://proceedings.iclr.cc/paper_files/paper/2025/hash/1b623663fd9b874366f3ce019fdfdd44-Abstract-Conference.html

Une revue récente organise les différents types de vérificateurs utilisés dans ce contexte.

### Référence

V. Venktesh et al., *Trust but Verify! A Survey on Verification Design for Test-time Scaling*, 2025.  
https://arxiv.org/abs/2508.16665

---

## Rapport avec Elenchos

Le test-time compute apporte un cadre expérimental très utile :

```text
plus de calcul
     ↓
plus de candidats
     ↓
plus de vérification
     ↓
meilleure sélection ?
```

Mais Elenchos ne cherche pas seulement :

> comment obtenir une meilleure précision avec plus de calcul ?

Il cherche plutôt :

> **quelle structure de calcul supplémentaire produit de l'information indépendante sur l'erreur ?**

Le coût d'inférence devra donc être explicitement contrôlé dans les expériences.

---

# 17. Vérificateurs déterministes : une catégorie qualitativement différente

Une distinction centrale devra être faite entre deux types de vérification.

## 17.1 Vérification probabiliste

```text
LLM A produit P
LLM B juge P
```

Le juge est lui-même faillible.

---

## 17.2 Vérification déterministe

```text
LLM produit un programme
        │
        ▼
    compilateur
        │
        ▼
 valide / invalide
```

ou :

```text
LLM produit 127 × 83 = 10441
        │
        ▼
     calculatrice
        │
        ▼
     vrai / faux
```

ou :

```text
plan
 │
 ▼
solveur de contraintes
 │
 ▼
satisfiable / impossible
```

Ces outils introduisent un canal d'information **épistémiquement différent**.

Leur erreur éventuelle n'est pas corrélée de la même manière avec celle du LLM.

Cela les rend particulièrement importants pour Elenchos.

---

# 18. Taxonomie provisoire des sources de redondance

Toutes les redondances ne se valent pas.

On peut provisoirement distinguer :

## Niveau R0 — répétition

```text
même modèle
même prompt
température différente
```

Faible indépendance.

---

## Niveau R1 — variation de raisonnement

```text
même modèle
prompts / trajectoires différents
```

Exemple : self-consistency.

---

## Niveau R2 — variation de rôle

```text
générateur
critique
juge
```

Même modèle possible, mais contexte fonctionnel différent.

---

## Niveau R3 — diversité de modèles

```text
Llama
Qwen
Gemma
Claude
GPT
...
```

Indépendance plus forte en apparence, mais les erreurs restent souvent corrélées.

---

## Niveau R4 — transformation du problème

```text
x
T1(x)
T2(x)
```

avec relations attendues entre résultats.

Exemple : metamorphic testing.

---

## Niveau R5 — représentation hétérogène

```text
texte
équation
graphe
programme
tableau
```

Une même information est encodée sous plusieurs formes.

---

## Niveau R6 — canal déterministe externe

```text
LLM
 │
 ├── compilateur
 ├── solveur
 ├── base de données
 ├── moteur de preuve
 └── calcul exact
```

Potentiellement très forte indépendance.

---

# 19. Matrice comparative

| Approche | Sans vérité terrain ? | Détection | Localisation | Correction | Sensible aux erreurs corrélées | Relation avec Elenchos |
|---|---:|---:|---:|---:|---:|---|
| Self-consistency | Oui | indirecte | Non | sélection | Très | baseline de redondance |
| Auto-évaluation | Oui | Oui | limitée | Non | Très | signal secondaire |
| Self-Refine | Oui | parfois | parfois | Oui | Très | boucle de correction |
| Reflexion | parfois | Oui | parfois | Oui | dépend du feedback | mémoire d'échec |
| Chain-of-Verification | Oui / partiel | Oui | Oui | Oui | moyenne | très proche |
| Multi-agent debate | Oui | Oui | Oui | Oui | forte | elenchos procédural |
| N-version programming | Oui | indirecte | faible | masquage | forte si fautes communes | diversité |
| Byzantine fault tolerance | Oui | fautes d'agents | agent / message | tolérance | modélisée | robustesse distribuée |
| Metamorphic testing | **Oui** | **Oui** | parfois | généralement non | dépend des relations | **très proche** |
| Verifier appris | nécessite entraînement | Oui | parfois | sélection | dépend du verifier | canal de scoring |
| Outil déterministe | Oui si propriété vérifiable | **forte** | souvent | parfois | faible avec LLM | ancrage externe |
| ECOC | Oui à l'inférence | Oui | Oui | **Oui** | selon classifieurs | analogue formel contrôlé |

---

# 20. Ce qui semble déjà connu

À ce stade, les affirmations suivantes ne peuvent pas constituer une contribution originale d'Elenchos :

### « Plusieurs réponses valent mieux qu'une »

Déjà largement étudié via self-consistency, ensembles et test-time compute.

### « Les LLM peuvent se critiquer »

Déjà largement étudié via Self-Refine, Reflexion et nombreuses variantes.

### « Plusieurs agents peuvent débattre »

Déjà étudié dans la littérature multi-agent.

### « Un LLM peut vérifier sa réponse avec des sous-questions »

Chain-of-Verification l'étudie explicitement.

### « On peut tester sans connaître le résultat attendu »

C'est précisément le problème traité depuis longtemps par le metamorphic testing.

### « On peut tolérer certains agents fautifs »

C'est le domaine historique de la tolérance aux fautes byzantines, maintenant appliqué aux systèmes multi-LLM.

---

# 21. Ce qui paraît encore intéressant à investiguer

Le positionnement potentiel d'Elenchos est plus précis.

## Q1 — Peut-on construire des contraintes sémantiques redondantes ?

Pas simplement demander plusieurs fois la même chose, mais produire intentionnellement plusieurs représentations liées par des invariants.

---

## Q2 — Peut-on mesurer leur indépendance effective ?

Une relation n'est utile que si sa vérification ne reproduit pas exactement la même erreur.

Il faudra donc étudier :

```text
corrélation des erreurs
information mutuelle
diversité des modèles
diversité des représentations
diversité des outils
```

---

## Q3 — Existe-t-il un analogue opérationnel du syndrome ?

On chercherait un vecteur :

```text
S(P) = [v1, v2, ..., vn]
```

où chaque `vi` représente la violation ou satisfaction d'une contrainte.

Puis :

```text
S(P) ≠ 0
```

indiquerait une incompatibilité.

Question beaucoup plus forte :

> certains motifs de syndrome permettent-ils de **localiser une classe d'erreur** ?

---

## Q4 — Peut-on caractériser des classes d'erreurs détectables ?

Exemple :

```text
erreurs arithmétiques
erreurs logiques
erreurs factuelles
erreurs de cohérence
erreurs de référence
erreurs de contraintes
```

Il serait probablement irréaliste de chercher immédiatement un correcteur universel.

En revanche, certaines familles peuvent posséder des invariants exploitables.

---

## Q5 — Peut-on caractériser des classes d'erreurs corrigibles ?

Détection :

```text
quelque chose ne va pas
```

Correction :

```text
voici ce qui est faux
et voici la reconstruction correcte
```

La seconde propriété est beaucoup plus exigeante.

---

# 22. Hypothèse centrale provisoire

Une formulation suffisamment prudente pourrait être :

> **Pour certaines classes de tâches, des représentations redondantes reliées par des contraintes suffisamment indépendantes peuvent fournir un signal de détection d'erreur supérieur à une redondance non structurée, à coût d'inférence comparable.**

Cette hypothèse est :

- falsifiable ;
- limitée ;
- mesurable ;
- compatible avec l'état de l'art ;
- et ne suppose pas qu'un code correcteur général existe.

---

# 23. Première expérience recommandée : EXP-001

La première expérience ne devrait probablement **pas** commencer par un système multi-agent complexe.

Elle devrait tester l'idée minimale :

> une contrainte structurée apporte-t-elle plus d'information qu'un simple vote ?

---

## 23.1 Tâches

Commencer par des problèmes dont la vérité terrain peut être obtenue **uniquement pour l'évaluation expérimentale**, par exemple :

- arithmétique ;
- logique propositionnelle ;
- petits problèmes algorithmiques ;
- transformations de chaînes ;
- contraintes simples.

La vérité terrain ne doit pas être fournie au protocole Elenchos.

Elle sert uniquement au chercheur pour mesurer les performances.

---

## 23.2 Baseline A — génération unique

```text
x → LLM → réponse
```

---

## 23.3 Baseline B — self-consistency

```text
x ──┬→ génération 1
    ├→ génération 2
    ├→ génération 3
    └→ génération N

          ↓
     majorité
```

---

## 23.4 Variante Elenchos

Pour chaque problème, construire au moins une transformation `T` et une relation attendue `R`.

```text
x ─────────────→ LLM ──→ y
│
└── T(x) ──────→ LLM ──→ y'
                         │
                         ▼
                    vérifier R(y,y')
```

Le protocole ne connaît pas la bonne réponse.

Il sait seulement si la relation attendue est satisfaite.

---

# 24. Exemple minimal de « bit de parité sémantique »

Supposons une question arithmétique :

```text
Q : 37 + 58 = ?
```

Le modèle répond :

```text
95
```

On génère une transformation :

```text
Q' : 58 + 37 = ?
```

La relation métamorphique attendue est :

```text
answer(Q) == answer(Q')
```

Cette relation détecte certaines erreurs, mais pas une erreur stable :

```text
Q  → 94
Q' → 94
```

Le test passe alors que la réponse est fausse.

On ajoute donc une seconde relation, par exemple une décomposition :

```text
37 + 58
=
37 + 50 + 8
```

Puis éventuellement une vérification déterministe.

L'objectif expérimental devient alors :

> comment augmente la probabilité de détection lorsqu'on ajoute différentes contraintes, et à quel coût ?

---

# 25. Métriques pour EXP-001

Il faut distinguer **qualité de la réponse** et **qualité du détecteur**.

Pour le détecteur :

- true positive rate ;
- false positive rate ;
- precision ;
- recall ;
- F1 ;
- AUROC si score continu ;
- calibration ;
- taux d'abstention.

Pour le système final :

- accuracy ;
- accuracy conditionnelle lorsque le protocole accepte ;
- risk-coverage curve ;
- coût en tokens ;
- nombre d'appels modèle ;
- latence ;
- coût monétaire éventuel.

---

# 26. Métrique particulièrement importante : risque sous couverture

Un protocole robuste devrait pouvoir s'abstenir.

On peut donc mesurer :

```text
coverage = fraction des réponses acceptées

risk = taux d'erreur parmi les réponses acceptées
```

L'objectif n'est pas nécessairement :

```text
répondre à tout
```

mais peut être :

```text
répondre lorsqu'on dispose de suffisamment d'indices
s'abstenir sinon
```

Cela correspond beaucoup mieux à l'objectif épistémique d'Elenchos.

---

# 27. Contrôle du coût

Toute comparaison avec self-consistency ou une baseline doit être réalisée à **budget d'inférence comparable**.

Sinon :

```text
protocole A : 1 appel
protocole B : 20 appels
```

et constater que B est meilleur n'apprend presque rien sur la qualité de la structure.

Le budget devrait donc être exprimé par exemple en :

```text
nombre d'appels
tokens générés
latence
coût monétaire
```

---

# 28. Risques méthodologiques

## 28.1 Fuite de vérité terrain

Le protocole ne doit jamais accéder accidentellement aux labels utilisés pour l'évaluation.

---

## 28.2 Juge LLM utilisé comme oracle caché

Si un modèle plus puissant décide simplement quelle réponse est correcte, l'expérience devient :

```text
« un meilleur LLM améliore un moins bon LLM »
```

et ne teste plus l'hypothèse d'Elenchos.

---

## 28.3 Corrélation des variantes

Changer uniquement la température n'implique pas indépendance.

---

## 28.4 Transformations invalides

Une relation métamorphique mal conçue peut signaler une erreur là où il n'y en a pas.

La validité des transformations devra être contrôlée.

---

## 28.5 Prompt leakage

Si une variante montre explicitement la réponse précédente au modèle, elle n'est plus indépendante.

---

## 28.6 Sélection a posteriori

Les relations et métriques doivent être définies avant l'examen des résultats principaux pour éviter de retenir uniquement celles qui donnent de bons résultats.

---

# 29. Proposition de vocabulaire initial

## Production

Une sortie générée par un agent.

## Claim

Une proposition atomique ou semi-atomique extraite d'une production.

## Vue

Une représentation d'une même information obtenue par une transformation donnée.

## Contrainte

Une relation attendue entre plusieurs vues.

## Vérificateur

Mécanisme évaluant une contrainte.

## Violation

Résultat indiquant qu'une contrainte n'est pas satisfaite.

## Syndrome élénctique

> **Terme expérimental provisoire.**

Vecteur ou structure représentant l'ensemble des violations observées entre plusieurs vues d'une même information.

Aucune équivalence mathématique avec un syndrome de code correcteur n'est encore revendiquée.

## Diorthosis

Procédure tentant de reconstruire une sortie meilleure à partir des observations et violations détectées.

---

# 30. Positionnement provisoire d'Elenchos

Après cette première revue, le projet ne semble pas devoir se positionner comme :

> un nouveau framework de débat multi-agent.

Ni comme :

> une nouvelle technique d'autocorrection par prompting.

Ni comme :

> une simple application de la majorité à plusieurs modèles.

Le positionnement potentiellement distinct est plutôt :

> **étudier de manière systématique la construction de redondances et de contraintes entre plusieurs représentations de productions LLM, afin de caractériser quelles classes d'erreurs peuvent être détectées, localisées ou corrigées sans accès direct à la vérité.**

Le metamorphic testing constitue actuellement le domaine voisin le plus évident.

La question supplémentaire d'Elenchos serait de savoir si ces relations peuvent être organisées en une structure suffisamment générale pour parler de :

- contraintes ;
- motifs de violation ;
- indépendance des canaux ;
- distance ;
- classes d'erreurs ;
- et éventuellement décodage.

---

# 31. Conclusion provisoire

L'intuition initiale d'Elenchos **n'est pas isolée de la littérature**.

Ses principaux composants existent déjà séparément :

- redondance → self-consistency ;
- critique → Self-Refine ;
- vérification structurée → Chain-of-Verification ;
- confrontation → multi-agent debate ;
- absence d'oracle → metamorphic testing ;
- agents fautifs → Byzantine fault tolerance ;
- diversité → N-version programming ;
- décodage robuste → error-correcting output codes ;
- recherche et sélection → test-time compute.

Mais cette convergence est justement intéressante.

Elle suggère qu'Elenchos peut être formulé non comme une nouvelle astuce de prompting, mais comme une question transversale :

> **quelles relations entre observations faillibles créent réellement de l'information sur l'erreur ?**

Et la question la plus ambitieuse reste ouverte :

> **peut-on construire quelque chose qui joue, pour certaines classes de tâches LLM, un rôle analogue à celui d'un syndrome dans un code correcteur ?**

C'est cette question qu'EXP-001 doit commencer à tester, avec le protocole le plus petit possible.

---

# 32. Références principales

1. Wang, X. et al. — *Self-Consistency Improves Chain of Thought Reasoning in Language Models*. ICLR 2023.  
   https://arxiv.org/abs/2203.11171

2. Kadavath, S. et al. — *Language Models (Mostly) Know What They Know*. 2022.  
   https://arxiv.org/abs/2207.05221

3. Madaan, A. et al. — *Self-Refine: Iterative Refinement with Self-Feedback*. NeurIPS 2023.  
   https://arxiv.org/abs/2303.17651

4. Shinn, N. et al. — *Reflexion: Language Agents with Verbal Reinforcement Learning*. 2023.  
   https://arxiv.org/abs/2303.11366

5. Dhuliawala, S. et al. — *Chain-of-Verification Reduces Hallucination in Large Language Models*. Findings of ACL 2024.  
   https://arxiv.org/abs/2309.11495

6. Du, Y. et al. — *Improving Factuality and Reasoning in Language Models through Multiagent Debate*. 2023.  
   https://arxiv.org/abs/2305.14325

7. Kamoi, R. et al. — *When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of Self-Correction of LLMs*. TACL 2024.  
   https://aclanthology.org/2024.tacl-1.78/

8. Zhang, Q. et al. — *Understanding the Dark Side of LLMs' Intrinsic Self-Correction*. ACL 2025.  
   https://aclanthology.org/2025.acl-long.1314/

9. Kim, E. M. et al. — *Correlated Errors in Large Language Models*. ICML 2025.  
   https://proceedings.mlr.press/v267/kim25e.html

10. Cho, S., Ruberto, S., Terragni, V. — *Metamorphic Testing of Large Language Models for Natural Language Processing*. 2025.  
    https://arxiv.org/abs/2511.02108

11. Lee, H. et al. — *Robust Multi-Agent LLMs under Byzantine Faults*. 2026.  
    https://arxiv.org/abs/2605.09076

12. Chen, K.-Y. et al. — *The Self-Correction Illusion: LLMs Correct Others but Not Themselves*. 2026.  
    https://arxiv.org/abs/2606.05976

13. Lamport, L., Shostak, R., Pease, M. — *The Byzantine Generals Problem*. ACM TOPLAS, 1982.  
    https://www.cs.cornell.edu/courses/cs614/1999sp/notes99/byzantine.html

14. Knight, J. C. — *N-Version Programming*. 2002.  
    https://onlinelibrary.wiley.com/doi/abs/10.1002/0471028959.sof219

15. Dietterich, T. G., Bakiri, G. — *Error-Correcting Output Codes: A General Method for Improving Multiclass Inductive Learning Programs*. 1991.  
    https://www.semanticscholar.org/paper/Error-Correcting-Output-Codes%3A-A-General-Method-for-Dietterich-Bakiri/2ce4103e5bc275498adc81c422777ea404b5e599

16. Snell, C. et al. — *Scaling LLM Test-Time Compute Optimally Can Be More Effective than Scaling Parameters for Reasoning*. ICLR 2025.  
    https://proceedings.iclr.cc/paper_files/paper/2025/hash/1b623663fd9b874366f3ce019fdfdd44-Abstract-Conference.html

17. Venktesh, V. et al. — *Trust but Verify! A Survey on Verification Design for Test-time Scaling*. 2025.  
    https://arxiv.org/abs/2508.16665
