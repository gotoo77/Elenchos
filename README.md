# Elenchos

> **Peut-on extraire une information fiable de productions faillibles de LLM sans connaître la vérité à l'avance ?**

Elenchos est un projet de recherche expérimental consacré à l'étude de protocoles capables de **détecter, localiser, tolérer ou corriger des erreurs produites par des grands modèles de langage (LLM)** sans disposer nécessairement d'un oracle connaissant déjà la bonne réponse.

Le projet part d'une analogie avec les **codes détecteurs et correcteurs d'erreurs**.

Dans un système de communication, la redondance et certaines contraintes structurelles permettent de détecter — et parfois de corriger — une information corrompue sans savoir à l'avance quels éléments ont été altérés.

Elenchos pose une question :

> **Un principe analogue peut-il être appliqué aux productions de modèles de langage faillibles ?**

---

## La question centrale

Supposons que plusieurs agents faillibles produisent des informations sur un même problème.

Nous ne savons pas :

- quel agent a raison ;
- si au moins un agent a raison ;
- si plusieurs agents partagent la même erreur ;
- si leurs erreurs sont indépendantes ou corrélées ;
- ni, dans le cas général, quelle est réellement la bonne réponse.

Peut-on néanmoins concevoir un protocole tel que les **relations entre leurs productions** révèlent une information exploitable ?

Autrement dit :

> Au lieu de demander **« Quel agent dit vrai ? »**, peut-on demander **« Quelle information reste récupérable même lorsque nous ne savons pas quel agent dit vrai ? »**

Cette distinction constitue le point de départ d'Elenchos.

---

## Pourquoi « Elenchos » ?

**Elenchos** (ἔλεγχος) est un terme grec ancien associé à l'examen, à la mise à l'épreuve et à la réfutation, notamment dans la démarche socratique.

Plutôt que de supposer qu'une affirmation est vraie, une démarche élénctique examine ses conséquences, la confronte à d'autres affirmations et recherche les incohérences.

Cette idée correspond à la posture méthodologique du projet :

> **Ne pas faire confiance à l'agent. Mettre à l'épreuve la structure de ce qu'il affirme.**

---

## L'analogie avec les codes correcteurs

Un simple vote majoritaire entre plusieurs LLM **n'est pas** un code correcteur d'erreurs.

Si cinq modèles produisent la même réponse fausse, leur accord ne suffit pas à rendre cette réponse vraie.

Pour que l'analogie avec les codes correcteurs devienne réellement pertinente, il faudrait identifier — s'ils existent — des équivalents de notions telles que :

- la redondance ;
- les contraintes ;
- la parité ;
- la distance ;
- les syndromes d'erreur ;
- les classes d'erreurs détectables ;
- les classes d'erreurs corrigibles ;
- le décodage.

L'existence d'équivalents pertinents pour les LLM constitue une **question de recherche**, et non une hypothèse tenue pour acquise.

---

## Quatre niveaux de robustesse

Elenchos distingue quatre objectifs d'ambition croissante.

### 1. Détection d'erreur

Le protocole peut-il déterminer qu'une réponse est probablement erronée, contradictoire ou insuffisamment étayée ?

```text
réponse
   │
   ▼
[ protocole ]
   │
   ├── plausible
   └── suspecte
```

### 2. Localisation d'erreur

Le protocole peut-il identifier **où** se situe probablement l'erreur ?

```text
affirmation
 ├── proposition A
 ├── proposition B  ← suspecte
 └── proposition C
```

### 3. Tolérance aux erreurs

Peut-on continuer à extraire une information utile malgré la présence de composants peu fiables ?

```text
productions faillibles
         │
         ▼
    [ protocole ]
         │
         ▼
 information exploitable
```

### 4. Correction d'erreur

Le protocole peut-il reconstruire une réponse meilleure à partir des informations disponibles ?

```text
information corrompue / incertaine
                │
                ▼
           [ protocole ]
                │
                ▼
        information corrigée
```

Le projet **ne suppose pas** que ces quatre niveaux soient tous atteignables.

Déterminer où se situent les limites fait partie du travail de recherche.

---

## Elenchos et Diorthosis

Le projet distingue deux notions apparentées.

### Elenchos

Examen, mise à l'épreuve, recherche de contradictions et localisation d'erreurs.

> **Quelque chose est-il faux ou incohérent, et pouvons-nous déterminer où ?**

### Diorthosis

Du grec *διόρθωσις* : correction, rectification.

> **Une fois une erreur ou une incertitude détectée, pouvons-nous reconstruire quelque chose de meilleur ?**

Un protocole peut donc être **élénctique** sans être **diorthotique**.

Cette distinction permet notamment de ne pas confondre **détection** et **correction**.

---

## Principes de recherche

Elenchos doit rester délibérément sceptique vis-à-vis de sa propre hypothèse.

### Aucun LLM n'est un oracle

Aucun modèle n'est considéré par défaut comme détenteur de la vérité.

Un modèle plus puissant peut être utilisé expérimentalement, mais sa réponse ne devient jamais silencieusement la « vérité terrain ».

### Le consensus n'est pas la vérité

L'accord entre agents peut constituer un indice.

Mais des erreurs corrélées peuvent conduire plusieurs agents à produire unanimement la même réponse fausse.

### L'indépendance compte

La redondance ne devient réellement informative que si les différentes observations apportent suffisamment d'information indépendante.

Comprendre la **corrélation des erreurs** peut donc être aussi important que mesurer la précision individuelle des modèles.

### Privilégier la vérification déterministe

Lorsqu'une affirmation peut être vérifiée par un mécanisme déterministe — compilateur, parseur, solveur, calculatrice, suite de tests, contrainte de base de données, etc. — cette vérification fournit une nature de preuve différente d'une opinion supplémentaire produite par un LLM.

### L'abstention est un résultat valide

Un protocole robuste doit pouvoir conclure :

> **Informations insuffisantes pour décider.**

Échouer à récupérer une information fiable est préférable à fabriquer artificiellement de la confiance.

### Les expériences doivent être falsifiables

Chaque protocole proposé doit préciser :

- quelle propriété il prétend améliorer ;
- par rapport à quelle référence ;
- dans quelles conditions ;
- comment le succès sera mesuré ;
- quel résultat réfuterait l'hypothèse.

---

## Directions de recherche

Parmi les mécanismes susceptibles d'être étudiés :

- échantillonnage indépendant ;
- diversité des modèles ;
- examen contradictoire structuré ;
- critique adversariale ;
- décomposition et recomposition ;
- vérification d'invariants ;
- tests métamorphiques ;
- validateurs déterministes ;
- suivi de provenance ;
- graphes de contradictions ;
- calibration de confiance ;
- transformations répétées ;
- analyse du consensus et du désaccord ;
- protocoles inspirés de la tolérance aux fautes byzantines ;
- modèles informationnels de la redondance.

Il s'agit de **directions de recherche**, et non de choix architecturaux déjà arrêtés.

---

## Première question expérimentale

Une première hypothèse volontairement limitée pourrait être :

> **À coût d'inférence comparable, une redondance structurée permet-elle de détecter davantage de réponses erronées qu'un simple vote majoritaire ?**

### Référence

```text
question
   │
   ├── LLM A ──┐
   ├── LLM B ──┼── vote majoritaire
   └── LLM C ──┘
```

### Candidat Elenchos

```text
question
   │
   ├── réponses indépendantes
   │
   ├── extraction des affirmations
   │
   ├── examen croisé
   │
   ├── contradictions / invariants
   │
   └── confiance ou abstention
```

Le but de cette expérience n'est pas de démontrer qu'Elenchos fonctionne.

Il est de déterminer :

> **La structure supplémentaire apporte-t-elle une information mesurable ?**

---

## Ce qu'Elenchos ne suppose pas

Elenchos ne part pas du principe :

- qu'un nombre suffisant de LLM finit nécessairement par produire la vérité ;
- qu'un modèle plus puissant peut servir d'oracle universel ;
- que le consensus implique la correction ;
- que toutes les erreurs sont détectables ;
- que toutes les erreurs détectables sont corrigibles ;
- qu'un analogue général des codes correcteurs existe nécessairement pour les LLM.

Au contraire, déterminer **où l'analogie cesse de fonctionner** constitue un résultat de recherche intéressant en soi.

---

## État du projet

**Exploratoire — prototype de recherche.**

À ce stade, aucune affirmation n'est faite quant à l'existence d'un protocole général de correction d'erreurs pour les LLM.

Le projet commence avec une intuition :

> **L'erreur n'est peut-être pas seulement un bruit à éliminer.**
>
> **La structure du désaccord, des contraintes et de la redondance peut elle-même contenir de l'information.**

Elenchos existe pour déterminer jusqu'où cette intuition résiste à l'expérimentation.

---

## Langue

La documentation initiale du projet est rédigée en **français**.

Une version anglaise pourra être proposée ultérieurement, lorsque le vocabulaire, les concepts et les premières hypothèses expérimentales auront suffisamment mûri.

---

## Licence

À déterminer.
