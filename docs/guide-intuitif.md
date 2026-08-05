# Elenchos — guide intuitif

> Comprendre l'idée avant les maths.

Ce document donne une lecture volontairement simple de la formalisation d'Elenchos. Il ne remplace ni `formalisation.md` ni les protocoles expérimentaux : il explique l'intuition qu'ils rendent rigoureuse.

---

## 1. Le problème

Un LLM répond à une question.

```text
question → LLM → réponse
```

Le problème est simple : si nous ne connaissons pas déjà la bonne réponse, comment savoir si le LLM vient de se tromper ?

Demander au modèle « es-tu sûr ? » n'ajoute pas nécessairement beaucoup d'information. Lui poser exactement la même question plusieurs fois peut aider, mais plusieurs générations peuvent partager la même erreur.

Elenchos explore une autre possibilité : **produire plusieurs vues différentes mais reliées du même problème, puis tester les relations qui devraient exister entre elles.**

---

## 2. Exemple minimal

Question initiale :

```text
37 + 58 = ?
```

Le modèle répond :

```text
95
```

Nous pouvons construire une autre vue du même problème :

```text
58 + 37 = ?
```

Supposons que le modèle réponde :

```text
94
```

Nous n'avons même pas besoin de calculer nous-mêmes `37 + 58` pour savoir qu'il existe un problème.

Nous connaissons une propriété de l'addition :

```text
37 + 58 = 58 + 37
```

Les deux réponses devraient donc être identiques.

Elles ne le sont pas.

**Une contrainte a été violée.**

---

## 3. Une vue

Une **vue** est une autre manière d'observer la même information.

Pour le problème précédent :

```text
vue A : 37 + 58
vue B : 58 + 37
vue C : 37 + 50 + 8
vue D : 2 × (37 + 58)
```

Le point important n'est pas d'obtenir beaucoup de réponses.

Le point important est que **nous savons quelque chose sur les relations que leurs réponses devraient respecter**.

---

## 4. Une contrainte

Une contrainte est simplement une règle attendue entre des vues.

Par exemple :

```text
C1 : réponse(A) = réponse(B)
```

Pour une autre transformation :

```text
C2 : réponse(D) = 2 × réponse(A)
```

Nous pouvons coder chaque résultat de vérification :

```text
0 = contrainte satisfaite
1 = contrainte violée
```

---

## 5. Le syndrome élénctique

Supposons trois contraintes :

```text
C1 : satisfaite
C2 : violée
C3 : satisfaite
```

On peut représenter ce résultat par :

```text
[0, 1, 0]
```

Ce vecteur est ce que nous appelons provisoirement un **syndrome élénctique**.

Il ne dit pas encore :

```text
la réponse est fausse
```

et encore moins :

```text
voici la bonne réponse
```

Il dit seulement :

```text
voici le motif des relations qui ne tiennent pas
```

La question scientifique devient alors : **ce motif contient-il réellement de l'information sur l'erreur ?**

---

## 6. Pourquoi des vecteurs apparaissent naturellement

Pour un problème, nous obtenons par exemple :

```text
s = [1, 0, 1]
```

Pour mille problèmes, nous obtenons mille vecteurs :

```text
[0, 0, 0]
[1, 0, 1]
[0, 1, 0]
[1, 1, 0]
...
```

Ils forment naturellement une matrice :

```text
        C1 C2 C3
P1       0  0  0
P2       1  0  1
P3       0  1  0
P4       1  1  0
...
```

Les lignes représentent les problèmes ou productions.

Les colonnes représentent les contraintes.

La matrice n'est donc pas ajoutée pour « faire des maths » : elle apparaît simplement parce que nous observons plusieurs contraintes sur plusieurs problèmes.

---

## 7. La première vraie question

Une fois cette matrice obtenue, l'expérimentateur connaît également — uniquement pour mesurer le résultat — quelles réponses initiales étaient réellement correctes ou fausses.

Il peut alors demander :

```text
les syndromes des réponses fausses
ont-ils une distribution différente
 des syndromes des réponses correctes ?
```

Par exemple, si l'on observait :

```text
correct → souvent [0,0,0]
faux    → souvent [1,0,1]
```

alors `[1,0,1]` deviendrait un signal intéressant.

Ce ne serait toujours pas une preuve absolue qu'une réponse particulière est fausse.

Ce serait une **information statistique sur son risque d'erreur**.

---

## 8. Pourquoi ce n'est pas juste du vote

Une baseline simple consiste à poser quatre fois la même question :

```text
37 + 58 ? → 95
37 + 58 ? → 95
37 + 58 ? → 94
37 + 58 ? → 95
```

La majorité répond `95`.

Elenchos utilise le même budget d'appels autrement :

```text
37 + 58 ?           → ...
58 + 37 ?           → ...
37 + 50 + 8 ?       → ...
2 × (37 + 58) ?     → ...
```

Puis il exploite les **relations connues entre les réponses**.

EXP-001 demande essentiellement :

> À coût comparable, cette redondance structurée détecte-t-elle mieux les erreurs qu'une simple répétition ?

---

## 9. Pourquoi une seule contrainte ne suffit pas

Prenons la commutativité.

```text
37 + 58 → 94
58 + 37 → 94
```

La contrainte est satisfaite :

```text
94 = 94
```

Pourtant les deux réponses sont fausses.

C'est fondamental.

**Une contrainte peut détecter certaines erreurs mais laisser passer les erreurs qui la préservent.**

Il faut donc étudier plusieurs contraintes qui échouent, idéalement, de manières différentes.

C'est ici que la notion d'indépendance devient importante.

---

## 10. Redondance nominale et redondance informationnelle

Quatre réponses ne signifient pas nécessairement quatre informations indépendantes.

```text
même modèle
même prompt
même raisonnement implicite
même biais
```

peuvent conduire à quatre variantes de la même erreur.

Elenchos distingue donc :

**Redondance nominale** : nous avons produit plusieurs sorties.

**Redondance informationnelle** : ces sorties ou vérifications apportent réellement des contraintes différentes sur l'information recherchée.

Cette distinction est probablement l'un des points les plus importants du projet.

---

## 11. Le parallèle avec les codes correcteurs

Dans un code correcteur classique, on ajoute volontairement de la redondance.

Les données valides doivent respecter certaines relations de parité.

Quand une transmission est altérée, certaines de ces relations cessent d'être satisfaites.

Le motif obtenu est appelé un **syndrome** et peut, dans certains codes, permettre de localiser puis corriger l'erreur.

Elenchos demande s'il existe, pour certaines classes de tâches, un analogue fonctionnel :

```text
information recherchée
        ↓
plusieurs vues structurées
        ↓
contraintes entre vues
        ↓
motif de violations
        ↓
syndrome élénctique
        ↓
   ? détection
        ↓
   ? localisation
        ↓
   ? correction
```

Le point d'interrogation est essentiel.

Nous ne savons pas encore si l'analogie tient au-delà de la métaphore.

---

## 12. Les trois marches de recherche

### Marche 1 — Détection

```text
Le syndrome aide-t-il à distinguer
une réponse correcte d'une réponse fausse ?
```

C'est EXP-001.

### Marche 2 — Localisation

Si la première marche fonctionne :

```text
certains motifs correspondent-ils
à certaines classes d'erreurs ?
```

Par exemple, un motif pourrait être davantage associé à une erreur de signe qu'à une erreur de calcul intermédiaire.

### Marche 3 — Correction

Seulement si les deux premières donnent un signal :

```text
le syndrome permet-il de choisir
ou reconstruire une meilleure réponse ?
```

C'est la partie **Diorthosis**.

---

## 13. Ce qu'un résultat négatif nous apprendrait

EXP-001 peut parfaitement échouer.

Si la redondance structurée ne fournit aucun signal supérieur à la répétition, plusieurs explications sont possibles :

- nos contraintes sont trop faibles ;
- leurs erreurs sont trop corrélées ;
- le domaine choisi ne permet pas ce type de structure ;
- le LLM préserve trop facilement les mêmes erreurs sous transformation ;
- ou l'intuition générale est simplement mauvaise.

Ce dernier résultat est autorisé.

Elenchos est une expérience, pas une conclusion déjà décidée.

---

## 14. La phrase à retenir

Si tout le reste devient flou, garder ceci :

> **Elenchos ne demande pas seulement plusieurs réponses. Il fabrique plusieurs observations reliées par des contraintes connues, puis étudie si le motif de leurs violations révèle quelque chose sur l'erreur sans avoir besoin de montrer la vérité au protocole.**

Et EXP-001 teste uniquement la première moitié de cette ambition :

> **la structure apporte-t-elle réellement plus d'information que la répétition ?**
