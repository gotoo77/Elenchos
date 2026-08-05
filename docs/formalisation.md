# Formalisation — Elenchos

> **Objectif : définir un vocabulaire et un modèle minimal permettant de transformer l'intuition d'un « code correcteur pour productions de LLM » en hypothèses falsifiables.**

**Statut :** document de travail initial  
**Projet :** Elenchos  
**Langue :** français  
**Date :** août 2026

---

## 1. Pourquoi formaliser avant d'implémenter

L'analogie avec les codes correcteurs est séduisante, mais elle peut devenir trompeuse si l'on importe trop vite leur vocabulaire sans disposer des structures mathématiques correspondantes.

Elenchos ne suppose donc pas qu'une réponse de LLM soit littéralement un mot de code, qu'une contradiction soit un bit erroné, ni qu'une distance de Hamming possède un équivalent naturel dans l'espace sémantique.

La formalisation cherche d'abord à répondre à une question plus modeste :

> **quelles observations supplémentaires et quelles relations entre elles peuvent apporter de l'information sur une erreur sans révéler directement la vérité recherchée ?**

Le modèle présenté ici est volontairement minimal et provisoire.

---

## 2. Univers du problème

Soit un problème ou une requête :

```text
x ∈ X
```

On suppose qu'il existe une propriété de correction associée à une production `y` :

```text
Correct(x, y) ∈ {0, 1}
```

Dans une expérience contrôlée, cette propriété peut être connue de l'évaluateur.

Mais le protocole Elenchos n'y a pas accès pendant son exécution.

On distingue donc explicitement :

```text
                protocole Elenchos
                       │
                       │ ne voit pas
                       ▼
                 Correct(x, y)
                       ▲
                       │
                       │ disponible seulement
                       │ pour l'évaluation
                  expérimentateur
```

Cette séparation est fondamentale : sinon un oracle caché rendrait triviale la détection d'erreur.

---

## 3. Production

Une **production** est une sortie générée par un agent à partir d'une entrée.

Soit un agent faillible :

```text
A : X → Y
```

Une production est :

```text
y = A(x)
```

`A` peut être :

- un LLM ;
- une instance particulière d'un LLM ;
- un agent doté d'un prompt ou d'un rôle ;
- éventuellement un autre composant probabiliste.

La notion de production ne présume rien de sa correction.

---

## 4. Claim

Une production textuelle peut contenir plusieurs affirmations.

On appelle **claim** une proposition suffisamment isolable pour pouvoir être confrontée à d'autres observations ou contraintes.

On peut représenter une production comme :

```text
y → {p1, p2, ..., pn}
```

L'extraction des claims peut elle-même être faillible.

Il faudra donc distinguer ultérieurement :

```text
erreur dans la production

vs

erreur dans l'extraction de sa structure
```

EXP-001 devra éviter autant que possible cette difficulté en utilisant des tâches dont les sorties sont simples et structurées.

---

## 5. Vue

Une **vue** est une observation d'une même information obtenue par un canal ou une transformation donnée.

Pour un problème `x`, on définit une transformation :

```text
T_i : X → X_i
```

puis une vue :

```text
v_i = A_i(T_i(x))
```

Une vue peut varier par :

- la formulation de la question ;
- la transformation du problème ;
- le modèle utilisé ;
- le rôle de l'agent ;
- la représentation demandée ;
- l'utilisation d'un outil externe.

Exemple :

```text
x  = « 37 + 58 = ? »

v1 = réponse directe
v2 = réponse à « 58 + 37 = ? »
v3 = décomposition « 37 + 50 + 8 »
v4 = résultat d'une calculatrice
```

Toutes ces vues portent sur une information liée, mais elles ne sont pas nécessairement équivalentes du point de vue de leur indépendance.

---

## 6. Contrainte

Une **contrainte** exprime une relation attendue entre une ou plusieurs vues.

On note :

```text
C_j(v_1, ..., v_k)
```

Dans le cas le plus simple :

```text
C_j ∈ {satisfaite, violée}
```

Une contrainte peut aussi produire un score continu :

```text
C_j(v_1, ..., v_k) ∈ [0,1]
```

Exemples :

```text
C_comm(v1, v2) := answer(v1) == answer(v2)
```

ou :

```text
C_compile(programme) := le compilateur accepte le programme
```

ou encore :

```text
C_equiv(forme_textuelle, forme_symbolique)
```

Une contrainte n'est utile que si sa satisfaction est attendue pour les productions correctes avec une probabilité suffisamment élevée.

---

## 7. Vérificateur

Un **vérificateur** est le mécanisme concret chargé d'évaluer une contrainte.

On distingue au moins :

### Vérificateur déterministe

Exemples :

- calculatrice ;
- compilateur ;
- solveur SAT/SMT ;
- parseur ;
- moteur de règles ;
- suite de tests.

### Vérificateur probabiliste

Exemples :

- LLM critique ;
- modèle juge ;
- classifieur appris.

Cette distinction est essentielle : le vérificateur peut lui-même introduire une erreur.

On peut donc noter :

```text
V_j(C_j, vues) → observation
```

et ne jamais confondre :

```text
contrainte théorique
```

avec :

```text
capacité réelle du vérificateur à l'évaluer
```

---

## 8. Violation

Une **violation** est l'observation qu'une contrainte attendue n'est pas satisfaite.

Pour une contrainte binaire :

```text
z_j = 0  si C_j est satisfaite
z_j = 1  si C_j est violée
```

Une violation n'implique pas nécessairement que la production principale est fausse.

Elle peut provenir :

- de la production principale ;
- d'une vue secondaire erronée ;
- d'une transformation invalide ;
- du vérificateur ;
- d'une contrainte mal spécifiée.

Ainsi :

```text
violation ≠ preuve automatique de fausseté
```

Elle constitue un **signal**.

---

## 9. Syndrome élénctique

On appelle provisoirement **syndrome élénctique** l'ensemble structuré des violations observées pour une production ou un problème.

Pour `m` contraintes binaires :

```text
S(x) = (z_1, z_2, ..., z_m)
```

Exemple :

```text
S(x) = (0, 1, 0, 1)
```

signifie que les contraintes 2 et 4 ont été observées comme violées.

Le terme « syndrome » est utilisé par analogie avec la théorie des codes, mais **aucune équivalence mathématique n'est revendiquée à ce stade**.

La première propriété recherchée est simplement :

```text
P(S(x) ≠ 0 | erreur) > P(S(x) ≠ 0 | correct)
```

Autrement dit, un syndrome non nul devrait être statistiquement informatif sur la présence d'une erreur.

---

## 10. Détection

Un détecteur élénctique est une fonction :

```text
D : S → {accept, suspect, abstain}
```

ou, plus généralement :

```text
D : S → [0,1]
```

produisant un score de suspicion.

La détection est utile si le syndrome permet de distinguer les productions correctes des productions erronées mieux qu'une baseline donnée.

Pour EXP-001, la baseline naturelle sera notamment la self-consistency à budget comparable.

---

## 11. Localisation

Détecter une erreur ne signifie pas savoir où elle se trouve.

On suppose qu'une production possède des composants :

```text
y = (p_1, p_2, ..., p_n)
```

Une procédure de localisation cherche à estimer :

```text
L(S, y) → sous-ensemble de {p_1, ..., p_n}
```

susceptible de contenir l'erreur.

La localisation devient possible seulement si différentes erreurs produisent des motifs de violation suffisamment distincts.

C'est ici que l'analogie avec un syndrome de code correcteur devient plus exigeante.

---

## 12. Classe d'erreur

Une **classe d'erreur** regroupe des erreurs partageant une propriété pertinente pour leur détection.

Exemples provisoires :

```text
E_arith
E_logique
E_contrainte
E_reference
E_factuelle
E_transformation
```

Une formalisation utile doit éviter la catégorie trop vague :

```text
« hallucination »
```

car deux erreurs linguistiquement similaires peuvent avoir des structures de vérification très différentes.

On cherchera plutôt à définir les classes par les **invariants qu'elles peuvent violer**.

---

## 13. Détectabilité d'une classe d'erreur

Soit une classe d'erreur `E`.

Intuitivement, `E` est détectable par un ensemble de contraintes `C` si les erreurs de `E` modifient suffisamment souvent le syndrome observé pour être distinguées des productions correctes.

Une définition expérimentale simple peut être :

```text
TPR_E(C) > seuil
```

sous une contrainte de faux positifs :

```text
FPR(C) < seuil
```

La détectabilité n'est donc pas absolue : elle dépend de :

- la famille de tâches ;
- l'agent ;
- les transformations ;
- les contraintes ;
- les vérificateurs ;
- les seuils acceptables.

---

## 14. Correction / Diorthosis

Une procédure de correction reçoit les productions et leur syndrome :

```text
R(x, vues, S) → y'
```

avec l'objectif :

```text
P(Correct(x, y')) > P(Correct(x, y))
```

La correction est plus forte que la détection.

Un protocole peut très bien savoir :

```text
« quelque chose ne va pas »
```

sans disposer de suffisamment d'information pour produire :

```text
« voici la bonne réponse »
```

Elenchos considère donc l'abstention comme une sortie légitime.

---

## 15. Redondance nominale et redondance informationnelle

Supposons deux vues :

```text
v1 = A(x)
v2 = A(x)
```

obtenues par deux échantillonnages.

Il existe deux sorties, donc une redondance nominale.

Mais si leurs erreurs sont fortement corrélées, l'information nouvelle apportée par `v2` peut être faible.

On distingue donc :

### Redondance nominale

Nombre de productions ou de canaux observés.

### Redondance informationnelle

Quantité d'information nouvelle apportée par ces observations relativement à la propriété recherchée.

Cette seconde notion est centrale mais n'est pas encore formalisée de manière satisfaisante.

---

## 16. Indépendance des erreurs

L'indépendance parfaite est probablement irréaliste pour les LLM.

On s'intéresse plutôt à la dépendance conditionnelle des erreurs.

Pour deux vues `v_i` et `v_j`, on peut observer :

```text
P(E_i ∩ E_j)
```

et comparer cette valeur à :

```text
P(E_i) P(E_j)
```

Si :

```text
P(E_i ∩ E_j) >> P(E_i)P(E_j)
```

les erreurs sont positivement corrélées.

Une contrainte utile devrait idéalement relier des canaux dont les modes d'échec ne sont pas parfaitement communs.

---

## 17. Une notion provisoire de gain élénctique

Pour comparer une redondance structurée à une baseline, on peut définir expérimentalement un gain :

```text
G = performance(D_structuré) - performance(D_baseline)
```

à budget d'inférence comparable.

La performance peut être mesurée par :

- AUROC ;
- F1 ;
- risque sous couverture ;
- précision à couverture fixée ;
- taux de détection à faux positifs fixés.

La question minimale d'EXP-001 devient :

> **G est-il positivement et reproductiblement supérieur à zéro pour au moins une classe de tâches et une famille de contraintes ?**

---

## 18. Modèle minimal d'EXP-001

On peut maintenant écrire le protocole abstrait minimal.

### Entrée

```text
x
```

### Production principale

```text
y_0 = A_0(x)
```

### Vues redondantes

Pour `i = 1..n` :

```text
x_i = T_i(x)
y_i = A_i(x_i)
```

### Contraintes

Pour `j = 1..m` :

```text
z_j = V_j(C_j(y_0, ..., y_n))
```

### Syndrome

```text
S(x) = (z_1, ..., z_m)
```

### Décision

```text
D(S(x)) → accept / suspect / abstain
```

### Évaluation externe

Uniquement après la décision :

```text
Correct(x, y_0)
```

est révélé à l'expérimentateur pour calculer les métriques.

---

## 19. Cas limite : une contrainte parfaite

Si l'on dispose d'un vérificateur déterministe capable de décider directement :

```text
Correct(x, y)
```

alors Elenchos devient inutile pour cette propriété.

Exemple :

```text
37 + 58 = 94
```

peut être vérifié directement par une calculatrice.

Pourquoi alors utiliser l'arithmétique dans EXP-001 ?

Parce qu'elle permet de disposer d'une vérité terrain fiable pour **mesurer** le protocole, tout en interdisant volontairement à celui-ci l'accès à l'oracle direct.

Le but d'EXP-001 n'est pas de construire la meilleure calculatrice du monde.

Il est de tester le mécanisme dans un environnement où l'on peut savoir précisément quand il échoue.

---

## 20. Cas limite : consensus faux

Supposons :

```text
v1 = faux
v2 = faux
v3 = faux
```

avec :

```text
v1 = v2 = v3
```

La self-consistency possède un consensus maximal.

Mais si une transformation indépendante produit :

```text
C(v1, v4) = violation
```

alors la redondance structurée possède une information que le vote ne possède pas.

C'est exactement le type de situation qu'EXP-001 doit chercher à provoquer et mesurer.

---

## 21. Cas limite : syndrome nul mais réponse fausse

Un système peut produire :

```text
S(x) = 0
```

alors que :

```text
Correct(x, y) = 0
```

Cela correspond à une **erreur non détectée par l'ensemble actuel de contraintes**.

Cette possibilité doit être considérée comme normale.

Un syndrome nul signifie seulement :

> aucune des contraintes observées n'a détecté d'incompatibilité.

Il ne signifie jamais :

> la réponse est prouvée vraie.

Cette distinction est fondamentale.

---

## 22. Cas limite : syndrome non nul mais réponse correcte

Inversement :

```text
S(x) ≠ 0
```

peut survenir alors que la production principale est correcte.

Causes possibles :

- vue secondaire fausse ;
- transformation invalide ;
- vérificateur faillible ;
- contrainte trop forte ;
- ambiguïté de représentation.

Le syndrome doit donc être interprété probabilistiquement, sauf dans des sous-domaines où des garanties plus fortes peuvent être établies.

---

## 23. Ce qui distinguerait réellement Elenchos d'un ensemble de heuristiques

Un système composé de nombreux prompts de critique peut fonctionner sans constituer une théorie intéressante.

Pour dépasser ce stade, Elenchos devrait progressivement permettre de répondre à des questions comme :

1. Quelle classe d'erreur une contrainte vise-t-elle ?
2. Quel est son taux de détection ?
3. Quel est son taux de faux positifs ?
4. Avec quelles autres contraintes ses erreurs sont-elles corrélées ?
5. Quel gain marginal apporte-t-elle ?
6. Certains motifs de violations sont-ils associés à certaines classes d'erreurs ?
7. Peut-on retirer une contrainte sans perdre d'information ?
8. À quel coût cette information est-elle obtenue ?

Autrement dit, l'objectif n'est pas seulement :

```text
« faire réfléchir davantage le modèle »
```

mais :

```text
« caractériser l'information apportée par chaque redondance »
```

---

## 24. Ce qui manque encore à l'analogie avec un véritable code correcteur

À ce stade, nous n'avons pas défini :

- un espace de messages ;
- un encodage canonique ;
- un ensemble de mots valides ;
- une distance sémantique possédant les propriétés nécessaires ;
- une matrice de contrôle ;
- une capacité de correction garantie ;
- un algorithme général de décodage.

Il serait donc prématuré de parler d'un **code correcteur sémantique** au sens mathématique.

Le terme reste une intuition génératrice de questions.

---

## 25. Hypothèse H1 — détection

Première hypothèse falsifiable proposée :

> **H1 — À budget d'inférence comparable, au moins une famille de contraintes relationnelles structurées permet de mieux détecter les réponses incorrectes qu'un vote de self-consistency sur une famille de tâches contrôlée.**

Hypothèse nulle :

> **H0 — À budget comparable, la redondance structurée n'apporte aucun gain reproductible de détection par rapport à la baseline.**

Cette formulation permet un résultat négatif parfaitement acceptable.

---

## 26. Hypothèse H2 — syndrome et classe d'erreur

Une hypothèse plus ambitieuse, qui ne doit être testée qu'après H1 :

> **H2 — Certaines classes d'erreurs produisent des distributions de syndromes suffisamment distinctes pour permettre une localisation ou une classification meilleure que le hasard.**

Si H2 échoue, le syndrome peut rester utile pour la détection sans permettre la localisation.

---

## 27. Hypothèse H3 — correction

Hypothèse encore plus forte :

> **H3 — Pour certaines classes d'erreurs, les informations contenues dans les vues et le syndrome permettent de reconstruire une réponse correcte plus souvent qu'une nouvelle génération indépendante à coût comparable.**

H3 correspond au passage d'**Elenchos** à **Diorthosis**.

Elle ne doit pas être présupposée par le projet.

---

## 28. Ordre expérimental recommandé

Le programme de recherche minimal devient :

```text
H1 : détecter
 │
 ├── échec → comprendre pourquoi / réduire l'ambition
 │
 ▼
H2 : localiser / classifier
 │
 ├── échec → conserver éventuellement la détection
 │
 ▼
H3 : corriger
```

Cet ordre évite de construire un mécanisme de correction avant d'avoir démontré que les signaux utilisés contiennent réellement de l'information sur l'erreur.

---

## 29. Critère de survie de l'analogie

L'analogie avec les codes correcteurs mérite d'être conservée si elle produit au moins une conséquence expérimentale utile que l'on n'aurait pas obtenue en raisonnant simplement en termes de prompting ou d'ensemble.

Par exemple :

- conception systématique de contraintes ;
- mesure du gain marginal de redondance ;
- identification de syndromes caractéristiques ;
- caractérisation de classes d'erreurs détectables ;
- stratégie de décodage fondée sur les violations.

Si elle ne produit rien de ce type, elle devra être abandonnée ou reléguée au rang de métaphore pédagogique.

C'est un résultat acceptable.

---

## 30. Principe méthodologique central

Pour chaque composant ajouté au protocole, Elenchos doit poser la question :

> **Quelle information nouvelle cette opération apporte-t-elle sur l'hypothèse « la production est erronée » ?**

Si aucune réponse mesurable ne peut être donnée, le composant n'a pas encore de justification scientifique dans le protocole.

---

## 31. Prochaine étape

Cette formalisation est suffisante pour écrire un protocole expérimental minimal.

Le prochain artefact devrait être :

```text
docs/experiences/exp-001.md
```

Il devra figer avant implémentation :

- la famille de tâches ;
- les transformations ;
- les contraintes ;
- les baselines ;
- le budget d'inférence ;
- les métriques ;
- les critères de succès ;
- les critères de réfutation ;
- les données enregistrées pour permettre la reproduction.

À ce stade seulement, une implémentation devient justifiée.
