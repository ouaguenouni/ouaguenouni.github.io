# No-slop catalog — français
 
Patterns and words that signal LLM-generated French text. Each entry has a seriousness level. The system avoids these when producing script-bound prose and flags them when critiquing a draft, according to the level.
 
The flagged items are in French; the rationales are in English by design (the assistant reasons in English).
 
## Level legend
 
- `[HARDCORE]` — instant AI-detection signal. Never produce. Always flag.
- `[HIGH]` — strong tell. Avoid except where no good alternative exists. Always flag.
- `[MEDIUM]` — overused cliché. Prefer alternatives. Flag when an alternative would clearly be better.
- `[LOW]` — context-dependent. Fine in legitimate uses; counts as slop only as filler.
## How to add new items
 
Append a line in the relevant section: `- [LEVEL] "item" — rationale and context notes.` The system reads this file at the start of every conversation.
 
---
 
## A. Sentence-structure clichés
 
- [HARDCORE] "non seulement X, mais aussi Y" — covered by RF4. The single most identifiable LLM structure, direct equivalent of "not only X but also Y".
- [HARDCORE] "non pas X, mais (bien) Y" — variant of the not-only family.
- [HARDCORE] "ce n'est pas X, c'est Y" / "il ne s'agit pas de X, mais de Y" — dramatic-reversal cliché. Instant tell.
- [HARDCORE] "plus qu'un simple X, c'est Y" / "bien plus qu'un X" — "more than just X" variant.
- [HARDCORE] "loin d'être X, Y" — "far from being X" reversal. Same family.
- [HARDCORE] "X n'est pas seulement Y, c'est aussi Z" — formal-register variant of the not-only family.
- [HIGH] "la question n'est pas de savoir si X, mais (de savoir si) Y" — pseudo-rhetorical setup, almost always slop.
- [HIGH] "au cœur de X se trouve Y" / "au fond, X est Y" / "fondamentalement, X est Y" — pseudo-essence framing.
- [HIGH] "il convient de noter que X" / "il est important de noter que X" / "notons que X" — meta-instruction to the listener. If it's worth noting, just note it.
- [HIGH] "il n'est pas exagéré de dire que X" / "on peut sans risque affirmer que X" — telegraphs that it probably is exaggeration.
- [HIGH] "X joue un rôle clé / crucial / central / déterminant / primordial dans Y" — vague-role construction. Replace with a specific verb.
- [HIGH] "X ouvre la voie à Y" / "X ouvre la porte à Y" — metaphor cliché.
- [HIGH] "X représente un changement de paradigme / une révolution / une nouvelle ère" — hype escalation.
- [HIGH] "il va sans dire que X" — and yet you said it.
- [HIGH] "force est de constater que X" — formal slop construction, extremely common in French AI prose.
- [MEDIUM] "X représente un(e) Y" (when X simply is Y) — abstraction inflation.
- [MEDIUM] "X constitue un(e) Y" (when X is a Y) — over-formal "constitue". Sometimes legitimate.
- [MEDIUM] "X est, à bien des égards, Y" — empty hedge with false depth.
- [MEDIUM] "En conclusion, X" / "Pour résumer, X" / "En somme, X" / "En définitive, X" when a summary is unwarranted.
- [MEDIUM] "que ce soit X ou Y, Z" when X and Y are decorative rather than exhaustive.
- [LOW] "comme nous l'avons vu, X" / "comme évoqué plus haut" — sometimes legitimate; slop when reflexive.
## B. Single overused words
 
- [HARDCORE] "plonger" / "plongeons (dans)" / "plongée (dans)" — the canonical French "delve into" / "let's dive in" tell. Spotted immediately.
- [HARDCORE] "tapisserie" (metaphorical, "une riche tapisserie de") — almost always slop.
- [HARDCORE] "une véritable mine d'or (de)" — treasure-trove marketing slop.
- [HIGH] "univers" used as a vague container ("dans l'univers de X") — French "realm".
- [HIGH] "monde" used metaphorically ("dans le monde de X") — slop opener. Literal world is fine.
- [HIGH] "paysage" used metaphorically ("le paysage de X", "le paysage actuel") — slop. Literal geography is fine.
- [HIGH] "voyage" used metaphorically ("un voyage à travers X") — particularly egregious tell.
- [HIGH] "véritable" as an intensifier ("un véritable bouleversement") — filler emphasis.
- [HIGH] "incontournable" — overused for "essentiel" / "à voir".
- [HIGH] "fascinant" / "captivant" — overused manufactured enthusiasm; show why it's interesting instead.
- [HIGH] "révolutionner" / "révolutionnaire" / "transformer" (hype sense) — hype verbs.
- [HIGH] "fluide" / "sans accroc" / "sans couture" — vague positive, French "seamless".
- [HIGH] "myriade" — pretentious for "beaucoup".
- [HIGH] "pléthore" — pretentious for "beaucoup".
- [HIGH] "naviguer" used metaphorically ("naviguer dans la complexité") — slop.
- [HIGH] "primordial" / "capital" (adjective) — pretentious for "important". Be specific about the importance.
- [HIGH] "se lancer dans" / "embarquer dans" (hype sense) — pretentious for "commencer".
- [MEDIUM] "écosystème" outside biology or actual systems — metaphor slop.
- [MEDIUM] "exploiter" / "tirer parti de" — legitimate in technical use ("exploiter la symétrie du problème"); slop in vague uses ("exploiter le potentiel").
- [MEDIUM] "crucial" / "essentiel" / "fondamental" / "déterminant" / "central" — strong-modal slop where the specific reason would be better.
- [MEDIUM] "pertinent" — vague positive. Name the relevance.
- [MEDIUM] "nuancé" — frequently implies depth without showing it.
- [MEDIUM] "façonner" — overused for "former" / "influencer".
- [MEDIUM] "incarner" — overused for "représenter".
- [MEDIUM] "mettre en lumière" / "éclairer" — pretentious for "montrer" / "expliquer".
- [MEDIUM] "souligner" when "montrer" or "appuyer" would do.
- [MEDIUM] "décortiquer" — overused French essay verb for "analyser" / "détailler".
- [MEDIUM] "se pencher sur" — overused for "examiner" / "étudier".
- [MEDIUM] "approfondir" — fine literally; slop in the "delve deeper" sense.
- [MEDIUM] "regorger de" / "foisonner de" / "foisonnant" — "teeming with", overused.
- [MEDIUM] "de pointe" / "à la pointe de" used loosely. "État de l'art" is acceptable as a precise benchmark term; slop when loose.
- [LOW] "robuste" — legitimate technical term (stats, optimisation, ML). Slop only in vague uses ("solution robuste") where "fiable" or specifics would be better.
- [LOW] "riche" — legitimate ("une littérature riche sur le sujet"); slop in "une riche histoire / tapisserie".
## C. Multi-word phrases
 
- [HARDCORE] "une véritable mine d'or de X" — see B.
- [HIGH] "dans l'univers de X" — slop opener.
- [HIGH] "dans le monde de X" — slop opener.
- [HIGH] "dans un monde où X" — extremely common French AI / video-essay opener.
- [HIGH] "à l'ère de X" / "à l'ère du numérique" — French "in today's landscape" opener.
- [HIGH] "de nos jours" / "aujourd'hui plus que jamais" — filler opener and hype.
- [HIGH] "une plongée au cœur de X" — French "deep dive" framing.
- [HIGH] "offre un éclairage précieux sur X" / "apporte un regard neuf sur X" — French "provides valuable insights into".
- [HIGH] "offre une perspective unique sur X" — slop construction.
- [HIGH] "à la fin de la journée" — direct calque of "at the end of the day"; especially bad. "Au final" / "en fin de compte" are MEDIUM, see E.
- [MEDIUM] "un large éventail de" / "une multitude de" / "tout un panel de" — pretentious for "beaucoup de".
- [MEDIUM] "à la croisée de X et Y" / "à l'intersection de X et Y" — overused framing; sometimes legitimate.
- [MEDIUM] "l'interaction entre X et Y" / "le jeu entre X et Y" — overused.
- [MEDIUM] "un regard plus attentif sur X" / "un coup d'œil plus approfondi à X" — slop framing.
- [MEDIUM] "faire / jeter la lumière sur X" — pretentious for "montrer" / "expliquer".
- [MEDIUM] "combler le fossé entre X et Y" — overused metaphor.
- [MEDIUM] "la pierre angulaire de X" / "le socle de X" / "le fondement de X" — overused metaphors.
- [MEDIUM] "l'épine dorsale de X" — overused metaphor; sometimes legitimate ("l'épine dorsale du protocole").
- [MEDIUM] "acquérir une compréhension plus profonde de X" — verbose for "mieux comprendre X".
- [MEDIUM] "il est essentiel de prendre en compte X" — slop hedge.
- [MEDIUM] "ceci étant dit" / "cela étant" — transitional slop.
- [LOW] "une grande variété de" / "toute une gamme de" — often legitimate.
## D. Hedging tics
 
- [MEDIUM] "essentiellement" used as filler — when not actually pointing at an essence.
- [MEDIUM] "fait intéressant" / "chose intéressante" / "de manière intéressante" — telling the listener what to feel; show it.
- [LOW] "largement" — filler hedge in many uses; legitimate when scoping a claim.
- [LOW] "sans doute" / "vraisemblablement" — filler; legitimate when an actual argument follows.
- [LOW] "fondamentalement" — filler when not about fundamentals.
- [LOW] "intrinsèquement" — filler when no inherence is claimed.
- [LOW] "notamment" — filler emphasis when nothing notable is highlighted.
- [LOW] "significativement" — legitimate when quantified/statistical significance is established; filler otherwise.
- [LOW] "effectivement" — filler; legitimate meaning "in effect" / confirming something specific.
- [LOW] "relativement" — vague hedge unless a comparison is named.
## E. Transitional clichés
 
- [MEDIUM] "En substance," / "En essence," opener — filler.
- [MEDIUM] "Au final," / "En définitive," / "Finalement," / "En fin de compte," opener — filler unless a real conclusion follows.
- [MEDIUM] "En effet," used as filler — legitimate when confirming something specific.
- [MEDIUM] "Force est de constater que," opener — see A.
- [LOW] "De plus," — acceptable in moderation; flag when the third or fourth in a stretch.
- [LOW] "Par ailleurs," — same.
- [LOW] "En outre," / "De surcroît," — same; "de surcroît" is also stiff for spoken VO.
- [LOW] "Ainsi," — overused but sometimes legitimate.
- [LOW] "Cela dit," — overused but sometimes legitimate.
## F. Structural tics
 
- [MEDIUM] Three-item lists everywhere — the LLM compulsion to triplicate. Two items, or one, is often more honest.
- [MEDIUM] Tricolons with matched rhythm ("on propose, on prouve, on évalue") — formulaic cadence.
- [MEDIUM] Every beat ends with a manufactured "stinger" line — formulaic closing.
- [MEDIUM] Mirrored sentence structures across consecutive paragraphs — formulaic parallelism.
- [LOW] Paragraphs of uniform length — a tell in aggregate; flag only if a section is conspicuously regular.
## G. YouTube spoken-script tics (French VO)
 
New section for the script use case. These are French video-essay and voiceover clichés. They are slop in the script, not in Rick's chat.
 
- [HARDCORE] "Aujourd'hui, on va parler de X" / "Dans cette vidéo, nous allons voir X" — dead generic opener. The single most over-used French YouTube cold open.
- [HIGH] "Mais ce n'est pas tout !" — infomercial stinger.
- [HIGH] "Et c'est là que ça devient intéressant" / "et c'est là que tout bascule" — manufactured-suspense stinger.
- [HIGH] "Accrochez-vous" / "Préparez-vous, parce que X" — hype filler.
- [HIGH] "Spoiler :" used reflexively as a hook crutch.
- [HIGH] "Mais d'abord, un petit mot de notre sponsor" framing bolted into the content beat rather than placed deliberately — flag placement, not the sponsor read itself.
- [MEDIUM] "Like et abonne-toi" / "n'oublie pas de t'abonner" dropped mid-content — CTAs belong where the creator places them; flag only when reflexive or mid-beat.
- [MEDIUM] "Vous l'aurez compris" / "vous l'avez deviné" — filler.
- [MEDIUM] "Mais avant ça," / "Mais commençons par le commencement" — generic detour transition.
- [MEDIUM] "Croyez-moi" / "je peux vous l'assurer" — empty trust-me filler; earn it with the evidence instead.
- [MEDIUM] "Bref," as a written VO transition — note: this is in Rick's chat vocabulary, so flag it only inside a `script` block, never in chat.
- [LOW] "Imaginez un instant que X" — a legitimate framing device, but overused as a default opener.
---
 
## Notes on how this file is consulted
 
When producing script-bound prose, the system avoids HARDCORE and HIGH items unconditionally, prefers alternatives to MEDIUM items, and treats LOW items as acceptable except in obvious filler uses.
 
When critiquing a draft, the system flags HARDCORE and HIGH items wherever they appear, flags MEDIUM items when an alternative would clearly be better, and flags LOW items only when used as filler with no anchoring referent.
 
In conversational chat the file does not apply: Rick may use any of these in character.