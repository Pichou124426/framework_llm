# RAG Offensive Framework

Framework de simulation d'attaques offensives ciblant l'étape de retrieval des pipelines RAG (Retrieval-Augmented Generation), développé dans le cadre d'un stage en sécurité des infrastructures IA.

## Objectif

Documenter et simuler les vecteurs d'attaque connus visant le retriever d'une architecture RAG, à des fins de compréhension pratique et de préparation de mesures de défense.

## Périmètre

Ce framework couvre exclusivement les attaques ciblant l'étape de retrieval (base vectorielle, mécanismes de similarité, embeddings). L'indexation et la génération ne sont pas traitées, sauf lorsqu'une attaque initiée à l'indexation a un impact direct sur le retrieval.


## Infrastructure du projet
/attacks
  /corpus-poisoning       → touche M1, M2, M3
  /retrieval-hijacking    → touche M6
  /embedding-inversion    → touche M3, M6
  /prompt-injection-indirect → touche M7, M8
  /cross-context-leakage → touche M4, M8
  /dos-vector-store       → touche M3, M6
  /metadata-bypass        → touche M6, M7
  /toolchain-abuse        → touche Tx (transversal)