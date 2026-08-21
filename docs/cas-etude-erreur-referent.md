# Cas d’étude — Erreur de référent, prémisse latente et cascade cohérente

> **Comment un LLM peut-il produire un raisonnement localement solide, factuellement plausible et pourtant globalement hors sujet à partir d’une seule hypothèse non vérifiée ?**

**Statut :** observation exploratoire / cas d’étude  
**Projet :** Elenchos  
**Date :** août 2026  
**Nature :** incident conversationnel réel, non expérimental  

---

## 1. Résumé

Ce document décrit un cas concret dans lequel un LLM a résolu silencieusement une ambiguïté de référent, puis a construit un raisonnement cohérent sur cette hypothèse erronée.

L’utilisateur faisait référence à :

> « mon projet [...] qui serait l’équivalent d’un code correcteur pour les LLM »

Le modèle a interprété ce référent comme désignant **GFM**, alors que le projet visé était **Elenchos**.

L’erreur initiale n’était donc ni une hallucination factuelle grossière, ni une faute logique évidente. Le modèle disposait d’une hypothèse plausible, mais insuffisamment étayée. Il l’a néanmoins traitée comme acquise, puis a produit plusieurs paragraphes de raisonnement pertinents relativement à cette hypothèse.

Le résultat était intellectuellement cohérent, mais construit sur une prémisse fausse.

Ce cas suggère une classe d’erreurs particulièrement intéressante pour Elenchos :

> **une prémisse latente incertaine peut devenir silencieusement une prémisse tenue pour vraie, puis contaminer une cascade de raisonnements localement valides.**

Le problème principal n’est donc pas seulement de vérifier les conclusions. Il peut être nécessaire de **rendre visibles, tracer et réévaluer les prémisses implicites dont elles dépendent**.

---

## 2. L’incident

Le contexte portait sur :

- les erreurs de mesure ;
- la dépendance à une référence potentiellement fausse ;
- l’intérêt de croiser plusieurs contrôles ;
- les codes détecteurs et correcteurs d’erreurs ;
- la possibilité d’un analogue pour les LLM.

L’utilisateur a alors évoqué :

```text
« mon projet [...] qui serait l’équivalent d’un code correcteur pour les LLM »
```

Plusieurs interprétations étaient possibles dans l’historique conversationnel.

Une représentation minimale aurait pu être :

```text
H1 : le projet mentionné est GFM
H2 : le projet mentionné est un autre projet
```

L’information disponible ne permettait pas de conclure avec certitude.

Le comportement robuste aurait donc pu être :

```text
référent(project) = UNKNOWN
```

ou :

```text
H1 plausible mais non vérifiée
→ demander confirmation
```

ou encore :

```text
conserver plusieurs hypothèses en parallèle
→ rechercher une information discriminante
```

Le modèle a au contraire effectué implicitement :

```text
UNKNOWN
   ↓
GFM
   ↓
raisonnement
   ↓
analogies pertinentes
   ↓
conclusion cohérente
```

L’hypothèse n’a jamais été signalée comme telle.

---

## 3. Pourquoi cette erreur est intéressante

La plupart des mécanismes simples de détection d’hallucination risquent de mal traiter ce cas.

Une grande partie de la réponse peut être factuellement correcte :

```text
GFM possède telle propriété               ✓
les codes de Hamming fonctionnent ainsi   ✓
les erreurs corrélées sont dangereuses    ✓
la redondance seule ne suffit pas         ✓
```

Le défaut est situé plus haut dans l’arbre de dépendance :

```text
« le projet auquel l’utilisateur fait référence est GFM »   ✗
```

À partir de cette prémisse fausse, beaucoup de propositions dérivées peuvent rester valides conditionnellement.

On obtient donc une structure du type :

```text
                 prémisse latente fausse
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       raisonnement valide     faits locaux vrais
              │                     │
              └──────────┬──────────┘
                         ▼
               réponse très plausible
                         │
                         ▼
                  conclusion erronée
```

Ce cas est dangereux précisément parce qu’il ne ressemble pas à une erreur grossière.

---

## 4. Une erreur de référent avant d’être une erreur factuelle

On peut distinguer plusieurs classes d’erreurs :

- **erreur factuelle** : une proposition sur le monde est fausse ;
- **erreur logique** : une inférence est invalide ;
- **erreur de source** : une information est mal attribuée ;
- **erreur de prémisse** : le raisonnement part d’une hypothèse fausse ;
- **erreur de référent** : un terme ambigu est relié au mauvais objet ;
- **erreur d’autorité** : une source ou un agent est implicitement traité comme oracle ;
- **erreur de confiance** : le niveau d’incertitude réel est masqué par la forme de la réponse.

L’incident étudié relève principalement de la chaîne :

```text
erreur de référent
        ↓
prémisse latente fausse
        ↓
cascade cohérente
        ↓
confiance apparente excessive
```

Cette distinction importe pour Elenchos, car un protocole capable de détecter des contradictions factuelles locales peut ne rien voir ici.

---

## 5. Effacement de provenance épistémique

Le phénomène central peut être décrit comme une **perte de provenance épistémique**.

Une proposition apparaît initialement sous une forme proche de :

```text
claim:
    « le projet mentionné est GFM »

origin:
    inféré depuis le contexte

confidence:
    moyenne

verified:
    false
```

Après quelques étapes de raisonnement, elle est réutilisée comme si elle était :

```text
claim:
    « le projet mentionné est GFM »

origin:
    fait établi

confidence:
    élevée

verified:
    implicitement oui
```

Aucune nouvelle preuve n’a pourtant été ajoutée.

Le système a donc transformé silencieusement :

```text
inféré
```

en :

```text
établi
```

Ce mécanisme est particulièrement problématique dans les raisonnements longs : plus une prémisse est réutilisée, plus elle peut acquérir artificiellement l’apparence d’un fait confirmé.

---

## 6. Analogie avec une référence métrologique fausse

Ce cas rappelle la structure générale d’un problème de métrologie : une chaîne peut être extrêmement précise relativement à une référence erronée.

Schématiquement :

```text
référence fausse
      ↓
procédure précise
      ↓
résultats cohérents
      ↓
système précisément faux
```

Dans le cas conversationnel :

```text
référent supposé faux
        ↓
raisonnement cohérent
        ↓
analogies pertinentes
        ↓
réponse convaincante
        ↓
réponse globalement hors cible
```

La leçon pour Elenchos est importante :

> **la cohérence des étapes aval ne suffit pas si la référence amont n’a pas elle-même été contrôlée.**

---

## 7. Pourquoi un critique LLM générique peut échouer

Supposons qu’un premier modèle produise la réponse erronée :

```text
LLM A
  ↓
« le projet = GFM »
  ↓
texte cohérent
```

Puis qu’un second modèle reçoive seulement ce texte avec l’instruction :

```text
« critique cette réponse »
```

Le second modèle peut parfaitement conclure que :

- l’analogie avec les codes correcteurs est pertinente ;
- le raisonnement est bien structuré ;
- les affirmations locales sont plausibles ;
- les conclusions suivent correctement les prémisses fournies.

Il risque alors d’hériter du même référent sans le reconstruire indépendamment :

```text
LLM A : référent = GFM
          ↓
      texte cohérent
          ↓
LLM B : évalue le texte
          ↓
      « cohérent »
```

Il s’agit d’un **échec de mode commun** : le critique vérifie la cohérence du raisonnement sans réexaminer la prémisse qui structure le raisonnement.

Cela suggère une règle plus forte :

> **un vérificateur ne devrait pas seulement contrôler les inférences ; il devrait, lorsque c’est pertinent, reconstruire indépendamment les prémisses critiques dont elles dépendent.**

---

## 8. Dépendance critique et budget de vérification

Toutes les prémisses ne méritent pas le même niveau de contrôle.

On peut distinguer deux dimensions :

```text
confidence(p) = confiance dans la prémisse p
impact(p)     = quantité de raisonnement dépendant de p
```

Une prémisse devient particulièrement dangereuse lorsque :

```text
confidence(p) faible ou moyenne
ET
impact(p) élevé
```

Dans ce cas, continuer le raisonnement sans vérification peut coûter beaucoup plus cher que de résoudre l’ambiguïté immédiatement.

On peut imaginer un score de priorité de vérification :

```text
verification_priority(p)
    ∝ uncertainty(p) × downstream_impact(p)
```

Cette formule n’est pas proposée comme métrique finale, mais comme intuition opérationnelle :

> **plus une hypothèse est incertaine et structurante, plus son contrôle doit intervenir tôt.**

---

## 9. Trois stratégies possibles

### 9.1 Abstention locale

Lorsque le référent ne peut être résolu :

```text
UNKNOWN
→ demander une précision
```

Cette stratégie minimise le risque mais augmente les interruptions.

Elle ne doit donc probablement pas être déclenchée sur toute ambiguïté, mais sur les ambiguïtés à fort impact.

### 9.2 Branching d’hypothèses

Le système conserve plusieurs interprétations :

```text
                « mon projet »
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
       H1 = GFM            H2 = autre projet
          │                     │
    conséquences           conséquences
          │                     │
          └──────────┬──────────┘
                     ▼
         information discriminante
```

Le raisonnement n’est engagé définitivement qu’après discrimination suffisante.

### 9.3 Résolution indépendante

Un second mécanisme reçoit la requête originale et le contexte pertinent, mais **pas l’interprétation choisie par le premier raisonneur**.

Il tente de résoudre :

```text
resolve_reference("mon projet")
```

Si les deux résolutions divergent, le désaccord devient un signal exploitable.

---

## 10. Vers un syndrome de prémisse

Elenchos pourrait représenter certains signaux de risque sous forme d’un syndrome non nécessairement binaire.

Pour une prémisse critique `p` :

```text
S_p = (
    ambiguity,
    provenance,
    independent_support,
    downstream_impact,
    contradiction
)
```

Exemple conceptuel :

```text
ambiguity            = élevée
provenance           = inférence contextuelle
independent_support  = absent
downstream_impact    = élevé
contradiction        = non observée
```

L’absence de contradiction ne doit pas être interprétée comme une validation.

Le syndrome pourrait au contraire indiquer :

```text
PREMISE_UNDERDETERMINED
```

Un point important apparaît ici :

> **« aucun contrôle n’a échoué » n’est pas équivalent à « la prémisse a été vérifiée ».**

---

## 11. Vérification des prémisses plutôt que vote sur les conclusions

Un protocole naïf pourrait demander à plusieurs agents :

```text
« cette réponse est-elle correcte ? »
```

Puis effectuer un vote.

Mais si tous les agents héritent de la même prémisse implicite, le vote apporte peu d’information indépendante.

Une approche plus élénctique serait de décomposer :

```text
1. quelles prémisses critiques cette réponse utilise-t-elle ?
2. lesquelles sont explicitement fournies ?
3. lesquelles sont inférées ?
4. lesquelles sont vérifiées indépendamment ?
5. lesquelles ont un fort impact aval ?
6. quelles conclusions changeraient si une prémisse était fausse ?
```

Le protocole examine alors non seulement :

```text
Conclusion(response)
```

mais aussi le graphe :

```text
Premises → Claims → Inferences → Conclusions
```

---

## 12. Hypothèses de recherche dérivées

Ce cas suggère plusieurs hypothèses falsifiables.

### H-REF-1 — Détection

> Un protocole qui extrait explicitement les référents ou prémisses critiques incertaines détecte davantage de réponses globalement erronées qu’un critique évaluant uniquement le texte final.

### H-REF-2 — Impact

> Le produit approximatif `incertitude × impact aval` permet de prioriser les vérifications plus efficacement qu’une vérification uniforme de toutes les affirmations.

### H-REF-3 — Indépendance

> La reconstruction indépendante d’une prémisse à partir du contexte original fournit un signal plus discriminant que la critique d’un raisonnement qui contient déjà cette prémisse.

### H-REF-4 — Abstention

> Autoriser une sortie `UNKNOWN / ASK` sur les prémisses critiques réduit le taux d’erreur résiduel à couverture comparable.

### H-REF-5 — Cascades

> Les erreurs de prémisse produisent des cascades plus difficiles à détecter par cohérence locale que les erreurs factuelles isolées.

Ces hypothèses ne sont pas considérées comme établies.

---

## 13. Proposition d’expérience future

Ce cas pourrait motiver une expérience dédiée, sans nécessairement devenir immédiatement `EXP-002`.

Un jeu de tâches pourrait contenir des dialogues avec :

- plusieurs entités plausibles ;
- un référent pronominal ou nominal ambigu ;
- suffisamment de contexte pour qu’un mauvais référent produise une réponse plausible ;
- une vérité terrain connue de l’évaluateur mais cachée au protocole.

On pourrait comparer :

```text
Baseline A
    réponse directe

Baseline B
    réponse + critique générique

Elenchos C
    extraction des prémisses
    + résolution indépendante des référents critiques
    + abstention si sous-déterminé
```

Variables possibles :

- taux de mauvais référents non signalés ;
- taux de détection des erreurs de référent ;
- taux d’abstention ;
- risque résiduel parmi les réponses acceptées ;
- coût en appels et tokens ;
- profondeur moyenne de cascade avant détection.

Un corpus synthétique pourrait être utilisé en premier afin de contrôler exactement l’ambiguïté et la vérité terrain.

---

## 14. Limites de cette observation

Ce cas ne démontre rien à lui seul.

Il s’agit :

- d’un incident unique ;
- observé dans une conversation longue ;
- sans protocole pré-enregistré ;
- sans baseline ;
- sans contrôle expérimental ;
- sans mesure quantitative.

Il serait donc incorrect de conclure que la méthode proposée détecte effectivement cette classe d’erreurs.

La valeur de ce cas est différente : il fournit une **forme d’échec concrète** à transformer en hypothèse testable.

---

## 15. Implication conceptuelle pour Elenchos

La question initiale d’Elenchos est :

> **Peut-on extraire une information fiable de productions faillibles sans connaître la vérité à l’avance ?**

Ce cas ajoute une nuance : la production observable peut être localement excellente alors que son ancrage initial est faux.

Le système ne doit donc peut-être pas seulement chercher :

```text
« cette affirmation est-elle contradictoire ? »
```

mais aussi :

```text
« quelles hypothèses ont été nécessaires pour produire cette affirmation ? »
```

puis :

```text
« lesquelles ont été vérifiées, lesquelles ont seulement été inférées,
et lesquelles sont devenues silencieusement des faits ? »
```

La cible n’est pas nécessairement de produire un oracle de vérité.

Une ambition plus réaliste pourrait être :

> **empêcher qu’une prémisse critique, incertaine et non vérifiée puisse acquérir silencieusement le statut de fait sans laisser de trace détectable.**

---

## 16. Formulation compacte

Le cas peut être résumé ainsi :

```text
ambiguïté
   ↓
hypothèse plausible
   ↓
hypothèse non marquée
   ↓
réutilisation
   ↓
perte de provenance
   ↓
cascade cohérente
   ↓
confiance apparente
   ↓
erreur globale difficile à voir
```

Et la réponse élénctique candidate devient :

```text
ambiguïté
   ↓
prémisses explicites
   ↓
provenance + confiance
   ↓
impact aval
   ↓
vérification indépendante / branching / abstention
   ↓
signal de désaccord
```

Le point essentiel n’est pas d’interdire au modèle de faire des hypothèses.

Il est de distinguer durablement :

```text
supposé ≠ établi
```

et d’éviter qu’un raisonnement réussi transforme progressivement l’un en l’autre sans preuve supplémentaire.
