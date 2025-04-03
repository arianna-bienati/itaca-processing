---
Project:
  - "[[ITACA]]"
Date: 2025-03-04
tags:
  - ITACA/progress
Status: ongoing
Summary: Annotation guidelines for the IJCoL evaluation set
---
# ITACA-eval Annotation Guidelines

> [!IMPORTANT]
> **General procedure**\
> In the [Inception interface](https://all4ling.eurac.edu/inception/login.html) you will find **pre-annotated connectives**. The pre-annotation uses an extended version of the Lexicon of Italian Connectives (LICO, Feltracco et al. 2016) as the basis for string matching. Plain string matching is enhanced by rule-based filtering that exclude from the pre-annotated strings the strings that cannot be connectives because they have non-compatible PoS tags (e.g., _prima_ when it is an ADJ, _sia_ when it is a VERB) and dependency relations (e.g., _e_ when connects two NOUNs). All excluded tokens are retained in the Inception layer "02 - Connettivo problematico (Tint)".
> 
> 1. If the connective is pre-annotated:\
> 1.1 decide whether it is a connective or not following the guidelines, by selecting Yes/No in the 'Is connective' layer. All pre-annotated strings are set to 'Yes' by defauls. **Do not delete the pre-annotation! Just set it to 'No'**.\
> 1.2 decide the sense category according to the guidelines. Choose 1 category from the dropdown menu under the "Sense category" layer. It is not possible for this task to choose more than 1 category. Please choose the one that you think it is most representative of the sense of the connective. For polysemic connectives, if you are undecided between the more general and the more specific sense, go for the most specific sense.\
> 1.3 add comments on the "Comment" layer if needed.
> 
> 2. If the connective is not pre-annotated:\
> annotate the connective by selecting 1(+) word and follow the procedure above: Is connective: yes/no; sense category from the dropdown menu; add comment if needed.

## Is connective
**Is this a connective according to Ferrari's (2021, 2024) definition?**

Annotation layer: Is connective\
Type: Boolean (yes/no)

### Definition
We report here Ferrari's (2021) definition of connective and further specifications from the "Dizionario di linguistica del testo a uso delle scienze umane" (Ferrari, a cura di, 2024).

From Ferrari (2021: 145-146): *Che cosa sono i connettivi?* 
>Il termine connettivo indica ciascuna delle **forme linguistiche morfologicamente invariabili** che offrono istruzioni su come legare gli **eventi** evocati dal testo o gli **atti linguistici di composizione testuale** attraverso **relazioni logico-argomentative** quali la causa, la consecuzione, la riformulazione, l’esemplificazione, la concessione, l’opposizione ecc. La definizione combina dunque una caratteristica di tipo semantico-comunicativo –  l’istruzione offerta all’interlocutore  – con una caratteristica di tipo formale –l’invariabilità morfologica.

Here we have a 'positive' definition that identifies a:
* Formal criterion: morphologically invariable forms -> and probably also morphosyntactically invariable forms.
* Functional criterion: link events or linguistic acts of textual composition through discourse relations

>Da questa definizione conseguono **due dati di carattere negativo**. Il primo è che non vanno considerati connettivi elementi che, pur essendo parole grammaticali invariabili, non indicano relazioni logico-argomentative: si pensa paradigmaticamente agli introduttori delle subordinate completive (che, di ecc.) e a quelli delle subordinate relative. In questa prospettiva, non sono connettivi neppure le preposizioni che indicano relazioni tra entità semantiche di primo grado, come persone, animali, cose, astrazioni (il nostro istituto è subito dopo l’incrocio). Il secondo dato è che non vanno considerate connettivi quelle espressioni che, pur essendo associate a una relazione logico-argomentativa, sono morfologicamente variabili: da ciò discende che, per questo fatto, la conseguenza è che, la causa? ecc.

From Ferrari (2024: 51-52): *Connettivo*

> Combinando la caratteristica semantica del valore logico-argomentativo con la caratteristica formale dell'**invariabilità morfosintattica**, la definizione di connettivo ha due importanti conseguenze. La prima è che non vanno considerati connettivi elementi che, pur essendo parole grammaticali, invariabili, non indicano relazioni logico-argomentative: si pensi paradigmaticamente agli introduttori delle subordinate completive (*che, di* ecc.) e a quelli delle subordinate relative. La seconda conseguenza è che non vanno considerate connettivi quelle espressioni che, pur essendo associate a una relazione logico-argomentativa, sono morfologicamente variabili: *da ciò discende che*, *per questo fatto*, *la conseguenza è che*, *la causa?* ecc. In quest'ultimo caso, si può parlare di para-connettivi.

'Negative' definition: Are excluded from connectives
* relative pronouns and complementizers
* prepositions when introducing first order entities (Lyons, 1977)
* no morphologically (and morphosyntactically) variable expressions

> [!NOTE] 
> Not only there should be no variation at the word level (i.e., no possibility for inflection), but also no variation at the syntagm/phrase level (e.g., no possibility for insertion and possibly synonymic variation).
> A classical example is the prepositional phrase *per questo motivo*: it can be inflected (*per questi motivi*) and is not syntagmatically fixed, linguistic material can be inserted as in *per tutti questi motivi*. There is also some paradigmatic variation as in *per questa ragione, per questo fatto*.

#### Morphosyntactic categories:

>Per quanto riguarda la loro forma linguistica, i connettivi appartengono a classi morfosintattiche diverse. Possono essere congiunzioni o locuzioni congiuntive subordinanti (perché, se, mentre, quando ecc.); congiunzioni coordinanti (e, o, ma ecc.); avverbi o sintagmi nominali o preposizionali con funzione avverbiale (infatti, dunque, per esempio, di conseguenza, insomma, in ogni caso, tutto sommato, in particolare, ciononostante, difatti ecc.); preposizioni o locuzioni preposizionali (per, a causa di ecc.).

* CONJ (SCONJ or CCONJ)
* ADV (or MWE with ADV function)
* PREP (or MWE with PREP)

#### Relational component: *what are the 'arguments' of a connective*?
>Come indica la definizione iniziale, la relazione logico-argomentativa associata ai connettivi può collegare gli **eventi** evocati dal testo (azioni, atti, processi, accadimenti, stati), come nell’enunciato *Si sente male perché ha mangiato troppo*, o **atti linguistici di composizione testuale**, come per esempio quando si esprime una consecuzione inferenziale (*Non c’è la sua macchina, quindi è uscito*) o una rettifica (*mi pare un bel lavoro, anzi è perfetto*). Ci sono autori che per il primo caso parlano di «operatori» o di «connettivi semantici», mentre per il secondo di «connettivi pragmatici»: altrove si sceglie l’accezione ampia –  si parla cioè di connettivi tout court –, distinguendo solo quando è necessario.

>Le istruzioni offerte dal connettivo hanno una componente relazionale e una componente concettuale. Da una parte, esse indicano all’interlocutore di collegare il contenuto dell’**unità linguistica** in cui compaiono (**sintagma, frase, enunciato**) con il contesto, che a seconda dei casi sarà linguistico o extralinguistico;

* events
* linguistic acts of textual composition (inference, correction, etc.)

>[!IMPORTANT]
>The model states that connectives may also operate between propositions within the same UI (cfr. Ferrari 2014: 133; Ferrari/Lala/Zampese 2021: 108). Hence:\
>**Conjoined VPs**\
>Even though conjoined VPs are often not separate nucleai, we consider *e, o, ma* as a connectives even when the two coordinate clauses are merged into one UI. *Certo, come argomento di contro si potrebbe dire che non tutto ciò che è su internet è vero __o__ che tante informazioni sono veritiere solo per metà, ma ormai penso che tutti i miei coetanei riescano a riconoscere se un’informazione è sbagliata __e__ sappiamo tutti quali siti è meglio non confrontare.*\
>**Conjoined NPs**\
>Are connectives only if the SN encapsulate 'eventive' nouns, i.e., nouns that semantically express events. *Il 1 gennaio 2020 le autorità disposero la chiusura del mercato __e__ l’isolamento di coloro che presentavano segni e sintomi dell’infezione.*
>In other cases, even if the nouns are not first order entities (e.g., *un sentimento di libertà __e__ sollievo*, *attenzione __e__ memoria*), we don't consider them connectives as they are not relevant for the textual composition of the text.\
>**Conjoined Adjectives**\
>Coordinating conjunctions conjoining adjectives are __never__ connectives.\
>**Per + infinitive**\
>*per + infinitive* constructions are often not separate UI; however, they usually express a clear purposive sense, hence 'per' is considered a connective. *In data odierna ho il piacere di scriverle questa lettera __per__ esprimere la mia opinione a riguardo alla sua decisione, in seguito alla pandemia, di estendere la didattica digitale integrata al triennio delle scuole superiori, che entrerà in vigore dall’anno prossimo.*\
>**A causa di, grazie a, per**\
>When *a causa di, grazie a, per* introduce a cause, they are always considered connectives, because whatever comes after should be interpreted as processes or states: *Tutto questo però ultimamente mi è impossibile fare a causa della scuola* = scuola=attività scolastiche; *la società che sta già soffrendo per i danni che sono stati arrecati dalla pandemia* = danni=il fatto di avere danni (result state); *ci sarà una caduta nell’apprendimento per deficit di attenzione e memoria* deficit=il fatto di avere deficit (stato del possesso di deficit).

## Semantic category
**Which sense does the connective express?**\
To annotate only if the connective is a connective according to Ferrari's (2021,2024) definitions.

Annotation layer: Semantic category\
Type: Tagset (see below)

### The tagset from the PDTB-3
The PDTB-3 (Penn Discourse Treebank v.3) tagset is used for defining a closed class of senses to be assigned to connectives. The tagset of senses is organized hierarchically. The top level, or *class level*, has four tags representing four major semantic classes: “TEMPORAL”, “CONTINGENCY”, “COMPARISON” and “EXPANSION”. For each class, a second level of types is defined to further refine the semantics of the class levels. The original tagset has also a third level, but for our goals it seems too fine-grained. In what follows we synthesize the PDTB-3 guidelines (Webber et al. 2019) with helpers for the specific task of annotating an Italian dataset of student essays.
#### Temporal
Two situations are temporally connected
* **Synchronous**: some degree of temporal overlap between the events described (es. typically *mentre*, *quando*).
* **Asynchronous**: one event is described as preceding the other (es. typically *prima che/di*, *dopo*).
#### Contingency
The situation described by one argument provides the reason, explanation or justification for the situation described by the other
* **Cause**: situations described in Arg1 and Arg2 are causally influenced but are not in a conditional relation (es. typically *perché*, *quindi*). 
* **Condition**: one argument presents a situation as unrealized _(the antecedent_), which (when realized) would lead to the situation described by the other argument (*the consequent*) (es. typically *se*, *purché*).
* **Negative condition**: one argument (*the antecedent*) describes a situation presented as unrealized, which if it doesn’t occur, would lead to the situation described by the other argument (*the consequent*) (es. typically *altrimenti*, *a meno che*).
* **Purpose**: one argument presents an action that an AGENT undertakes with the purpose of the GOAL conveyed by the other argument being achieved (es. typically *affinché*).

>[!TIP]
>**The case of 'per'**\
>The PREP *per* is very difficult to filter out, so all *per* have been pre-annotated. Be particularly careful when deciding whether it is a connective according to Ferrari's definitions. It should be noted that *per* is often paired with an Infinitive to express purpose. However, this construction can also have other contingency meanings as in: *Ecco la situazione in cui mi trovo, per essere stato troppo buono* (CONTINGENCY:Cause). In these cases we consider it a connective, even though it is very likely that the whole construction (per + Inf) is conveying the CONTINGENCY meaning.

#### Comparison
* **Contrast**: at least two differences between Arg1 and Arg2 are highlighted (es. *al contrario*, *bensì*).
* **Similarity**: one or more similarities between Arg1 and Arg2 are highlighted with respect to what each argument predicates as a whole or to some entities it mentions (es. *allo stesso modo*).
* **Concession**: a causal relation expected on the basis of one argument is cancelled or denied by the situation described in the other (es. prototypically *tuttavia*).

>[!TIP]
>How to choose between Contrast and Concession?
>1. Are at least two explicit differences highlighted between the arguments?
>2. If no, select Concession.
>3. If yes, check whether a causal relation that is expected on the basis of one argument is denied by the other. (Test by paraphrasing with eng. *although*, it. *anche se* or *nonostante*)
>4. If yes, select Concession.
>5. If no, select, Contrast.

>[!TIP]
>**The case of 'viceversa'**\
>We decided to consider connective of contrast 'viceversa' only when it opens a UI/Utterance and not when it closes it. Es. *Gianni è bello. Viceversa Luca non lo è*: viceversa is considered as connective of contrast. *Luca ama Marco e viceversa*: not considered a connective.

#### Expansion
Relations that expand the discourse and move its narrative or exposition forward
* **Conjunction**: both arguments bear the same relation to some other situation evoked in the discourse. It indicates that the two arguments make the same contribution with respect to that situation or contribute to it together. It differs from most other relations in that the arguments don’t directly relate to each other, but to this other situation (es. prototypically *e*, *in più* at the start of a sentence).
* **Disjunction**: two arguments are presented as alternatives, with either one or both holding. As with Conjunction, Disjunction is used when both its arguments bear the same relation to some other situation evoked in the discourse, making a similar contribution with respect to that situation. While the arguments also relate to each other as alternatives (with one or both holding), they also both relate in the same way to this other situation (es. typically *o*, *oppure*).
* **Equivalence**: both arguments are taken to describe the same situation, but from different perspectives (es. typically *cioè*).
* **Instantiation**: one argument describes a situation as holding in a set of circumstances, while the other argument describes one or more of those circumstances (es. typically *ad/per esempio*).

>[!TIP]
>**The case of 'infatti'**\
>The connective 'infatti' is labeled in LICO as EXPANSION:Instantiation, however its meaning can also be well described in the realm of CONTINGENCY:Cause (it is usually used as justification). Ferrari (2014) lists it under 'relazione di motivazione'. We decide to align to Ferrari's proposal and we label 'infatti' with CONTINGENCY:Cause. We will use EXPANSION:Instantiation only when there are deviations in the way the connective is usually used.

> [!TIP]
> **The case of 'come'**\
> 'come' is labelled in LICO as only having the TEMPORAL:Synchronous relation. However it can serve at least one more sense, i.e., the one of Instantiation when used in pair with *per/ad esempio*. *A parer mio la Didattica Digitale limita molte cose, come ad esempio la bravura di uno studente la voglia di impegnarsi e ti toglie molte opportunità che solo da studente puoi fare*.
> "Sometimes the relation of Instantiation seems to lack the requirement of the eventive nature of the arguments, as in *Per poter seguire le lezioni dalla propria casa, è sicuramente necessario possedere un dispositivo elettronico, come ad esempio un computer o un cellulare, dotato di una buona connessione a internet.* (it is clear that a computer or a mobile phone are not events). However, following Manzotti, we identify a relation of textual composition: a computer or a mobile phone stands for [possessing] a computer or a mobile phone. Thus we are still in the presence of a fully-fledged logical-argumentative relation." (Pecorari, personal communication).

Translated with DeepL.com (free version)
 
* **Level-of-detail**: both arguments describe the same situation, but in less or more detail (es. typically *in conclusione*, *in sintesi*).

>[!NOTE]
>Under this category fall specialized connectives that have the function of summing up (es. *in breve*, *in sostanza*, *insomma*) and properly concluding (*in conclusione*).

* **Substitution**: arguments are presented as exclusive alternatives, with one being ruled out (es. typically *anziché*, *invece di*)
* **Exception**: one argument evokes a set of circumstances in which the described situation holds, and the other argument indicates one or more instances where it doesn’t (es. *eccetto*, *tranne*).
* **Manner**: the situation described by one argument presents the manner in which the situation described by other argument has happened or been done. Manner answers “how” questions such as “How were the children playing?”. While Manner may be the only relation that holds between two arguments, it is often the case that another sense (Purpose, Result or Condition) is taken to hold as well.

>[!TIP]
>LICO does not list any connectives under "Manner". The english PDTB-3 exemplifies manner relations as introduced by 'thereby' and 'by'. In Italian, 'by' with Manner sense, is usually translated by a gerund; 'thereby' is usually translated as 'in modo da' or 'così da'.\
>We follow LICO decision of annotating 'in modo da' and 'così da/così che' with sense CONTINGENCY:Cause:Result.

#### Useful resources:

Check prototypical/possible senses of connectives:
* [Treccani](https://www.treccani.it/vocabolario/)
* [De Mauro](https://dizionario.internazionale.it/)
* [Sabatini-Coletti](https://dizionari.corriere.it/dizionario_italiano/)

>[!TIP] 
>Dictionaries are not aligned with the PDTB senses, so only partial matches may be found. For an Italian resource aligned with the PDTB, please consider the [LICO](http://connective-lex.info/). Drawback is that this resource is more limited than the dictionaries and often do not contain examples or even senses for some of the connectives.

Detailed description of PDTB senses: 
* PDTB-3: [PDTB Annotation Manual 3.0](https://catalog.ldc.upenn.edu/docs/LDC2019T05/PDTB3-Annotation-Manual.pdf)
* (legacy) PDTB-2: [PDTB Annotation Manual 2.0](https://www.seas.upenn.edu/~pdtb/PDTBAPI/pdtb-annotation-manual.pdf)

### The procedure

**How to define the sense of the connective?**

From Ferrari (2021: 147):

> [...] dall’altra esse **codificano il concetto che definisce il tipo di relazione logico-argomentativa veicolata**: causa, consecuzione, motivazione, riformulazione ecc. Tale codificazione può essere povera o anche molto ricca. All’estremo inferiore troviamo per esempio la congiunzione *e*. Dal punto di vista lessicale, essa si limita a indicare che gli elementi semantici connessi vanno considerati come unitari e che il primo precede il secondo; **la natura concettuale della relazione** (susseguenza temporale, consecuzione, opposizione, concessione ecc.) **si definisce, per inferenza, a partire dal contenuto semantico degli elementi collegati e dal contesto linguistico e extralinguistico**. All’estremo superiore vi è per esempio il connettivo *tuttavia*. Dal punto di vista relazionale, esso indica che la connessione instaurata vige tra gli elementi esplicitamente collegati e uno o più contenuti impliciti; dal punto di vista concettuale, esso segnala la presenza di una relazione di concessione, cioè il fatto che tra il primo e il secondo connesso vi è una relazione di opposizione che si risolve a favore del secondo senza tuttavia negare la fondatezza, verità ecc. del primo. Tale opposizione, sempre mediata da un contenuto implicito, può essere diretta o indiretta. È diretta in un caso come *Maria mangia come un lupo, tuttavia è molto snella*, in cui emerge un implicito, contraddetto dal secondo connesso, secondo il quale ci si dovrebbe aspettare che Maria non sia snella; è indiretta in un’enunciazione quale *La casa è spaziosa, tuttavia è poco luminosa*: qui l’opposizione e la sua risoluzione si giocano infatti interamente a livello implicito: la prima proprietà, cioè spaziosa, conduce a una conclusione positiva quale ad esempio –  decide il contesto  –  val la pena di comprare la casa, mentre la seconda, cioè poco luminosa –  vincente agli occhi del locutore  – porta a una conclusione negativa: non vale la pena di comprare la casa.

As Ferrari (2021: 147) duly notes, to identify the sense carried by the connective it **is not enough to assign it to its prototypical meaning**. Its meaning must be inferred from the semantics of the arguments linked by the connective and the linguistic and extralinguistic context.

>[!TIP]
>**The case of 'e'**\
>The coordinate conjunction *e* is a highly polysemic connectives. Dictionaries and treebanks record this polysemy by assigning to it various senses, depending on the context in which the *e* is found. Here we attach a table with senses recorded by widely used Italian dictionaries.

| connettivo | Dictionaries labels   | PDTB                             | Treccani | Sabatini-Coletti | De Mauro | LICO |
| ---------- | --------------------- | -------------------------------- | -------- | ---------------- | -------- | ---- |
| e          | contemporaneità       | Temporal:Synchronous             |          | x                |          |      |
| e          | contiguità/aggiunta   | Expansion:Conjunction            | x        | x                | x        | x    |
| e          | contrasto             | Comparison:Contrast              | x        |                  | x        |      |
| e          | successione temporale | Temporal:Asynchronous:Precedence |          | x                |          | x    |
| e          | condizione            | Contingency:Condition            |          | x                |          |      |
| e          | conseguenza           | Contingency:Cause:Result         |          | x                |          |      |
| e          | scopo                 | Contingency:Cause:Result + goal  |          | x                |          |      |

>[!TIP]
>**The case of 'e' + CONTINGENCY:Cause connectives**\
>In Italian student essays is very common to find CONTINGENCY:Cause relations marked by a polysemic 'e' further specified by a more specialized connective (es. _e di conseguenza_, _e quindi_). In these cases, since the 'specific' meaning is carried by the more specialized connective, the 'e' should be labeled as simply EXPANSION:Conjunction. 

## Comment
This field is there to contain everything the annotator would like to point out: doubts on the belonging of the string to the connective class, doubts on the sense category or more fine grained information about the sense category, as well as semantic/syntactic problems with how the connective is used by the writer.

---
# References
- [ ] #todo add references
