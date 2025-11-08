---
title: Comprendre les cartes sémantiques
date: 22/10/2025
description: De la théorie à la pratique
---

*TLDR;* Une carte sémantique est un diagram qui contient les mots d’un vocabulaire et ou les mots les plus proches sur la carte sont proche sémantiquement.
On l’entraine en utilisant une base de données qu’on appelle “Corpus” qui contient des phrases.
Il y’a plusieurs techniques qui peuvent être employées pour construire une représentation sémantique, celle que j’explique s’appelle Word2vec et elle fonctionne en utilisant le postulat de “Plus deux mots apparaissent dans des contextes similaires plus ils sont proches sémantiquement”

## Introduction et intuition

Montre moi votre carte, je vous dirais ce que vous cherchez.

Les *word embeddings* — traduisons pudiquement par “cartes sémantiques” — occupent une place paradoxale dans le paysage de l’intelligence artificielle. Apparues sous les feux des projecteurs vers 2013 avec le fameux Word2Vec, elles fascinent les initiés, impressionnent les néophytes, et demeurent probablement l’un des outils les plus systématiquement mal compris de tout le domaine. Ce qui n’est pas rien, dans un secteur où la confusion fait presque office de sport national.

:::html plot_1.html :::
