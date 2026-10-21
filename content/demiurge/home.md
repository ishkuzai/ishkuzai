---
title: Demiurge
lead: A world-building engine. Choose a scale, set what you care about, and it grows the rest.
summary: Demiurge generates consistent worlds, from a star and its planets to the life, peoples, languages and names upon them, in layers, from a seed.
---
## What Demiurge is

Demiurge is a world-building engine. You choose a scale, which can be a star system, a planet, a continent, a kingdom, a people or a language. You set as much or as little as you like, and Demiurge generates the rest so that it is consistent with everything around it.

It is made for two kinds of user.

* **Game-masters and RPG designers**, who need a setting quickly and want its parts to fit together. Rivers should run where the land sends them, kingdoms should sit where people can farm, and the names should sound as if they come from one language. Everything Demiurge makes can be converted into game statistics.
* **World-builders and writers**, who want to look closely. You can follow the history of a planet from its formation, the tree of life that grew on it, the peoples who spread across it and the languages they speak, and stop anywhere to look in detail.

Behind both is a simulation of worlds and of evolution. The engine that makes a familiar fantasy kingdom can be turned towards science fiction: a red-dwarf planet with no moon, a biosphere that never learned to fly, a species whose language is played on pipes.

## How it thinks

### Worlds are grown, not drawn

A world is built from its beginning to its present, in layers. Each layer rests on the one below and reacts to it.

1. a **star**, and the cloud of gas it formed from;
2. the **planets**, their moons and belts, and the main world's day, year, seasons, tides and eclipses;
3. the main world's **geology**: its magnetic field, and plate tectonics that begin, move continents, assemble supercontinents and eventually stop;
4. its **air and climate**, then its **surface**: oceans, mountains, rainfall, habitats;
5. its **water**: rivers, lakes and marshes, worked out from the height of the land and the rain that falls on it;
6. **life**, if it arises: a chance, never a certainty;
7. the **history of life**, from the first cell to complex animals and plants, with a tree of descent and the niches each lineage fills;
8. **peoples**: their ways of life, technology, migrations and states;
9. **realms and settlements** laid over the land;
10. the **languages** spoken there, and the names of everything.

Each layer has requirements. Life can arise only where the conditions for it hold. Farming can be discovered only on fertile ground. A castle is reached only through a long chain of earlier fortifications, and only where rivals push people to build them.

### Two scales, space and time

Everything has a place in space and a place in time. **Space** runs from the cosmic to the very small: galaxy, star system, planet, continent, region (about the size of Wales), landscape, feature, zone (a stretch of country a day or two across) and subzone (a ford, a grove, a village). **Time** runs from aeons down to ages, and these are not fixed lengths: they are cut from what happened on that world, so a turbulent world has many short ages and a quiet one has a few long ones.

### Only what you look at is made in detail

An Earth-sized planet has hundreds of thousands of zones. Demiurge knows the whole world coarsely and works out the detail only where you look: where a realm reaches, where a name is needed, or wherever you ask. The rest stays wilderness until someone goes there.

### Procedural and guided

* **Procedural:** give Demiurge nothing but a number, the *seed*, and it generates everything. The same seed and settings always give the same world.
* **Guided:** fix whatever you care about with presets and locks (a Sun-like star, two moons, this vowel system, a kingdom of this size) and Demiurge builds the rest around it, recording which parts you chose and which it generated.

### Honest about what it knows

Where Demiurge uses real physics, it says so. Where a number is a judgement (how readily life arises, how fast an empire decays), it says that too. You can see what you can change without breaking anything.

## What you can make

| Scale | What you get |
|---|---|
| **Star system** | the star and its life cycle, the planets, moons, asteroid belts and dwarf planets; whether any world could support life; a schematic, maps, globes and a timeline |
| **Planet** | plates through time, continents, oceans, climate, seasons by latitude, habitats, rivers and lakes; a history from formation to the present age |
| **Life** | a tree of life with groups whose ranks are earned rather than assigned; each group's defining traits and range; food webs and niches; a browsable wiki of every group |
| **Land** | continents down to individual zones and the places inside them, with each zone's ground, height, temperature, rainfall and humidity, and how habitable it is |
| **Peoples and states** | thousands of years of cultural history: foragers, farmers and herders; technology from fire to steel, printing and gunpowder; states that rise, conquer, decay and fall |
| **Religion, myth and magic** | faiths and their gods, calendars and rites, myths and a mythic history, a lost civilisation and its ruins, the state of magic |
| **Realms** | realms, territories and districts over the land; frontiers on rivers and mountain ranges; towns at the crossings; hamlets to cities; roads, wars and the changing map |
| **Languages** | sounds shaped by the speakers' bodies, grammar from isolating to polysynthetic, politeness and gender, writing systems, a tree of descent, and names for every place, person, plant and animal in the same language |
| **Game statistics** | races, creatures, environments, skills, equipment and characters converted into a game's system |

## Two defaults, and your own

Demiurge has two ways to begin and room for your own. All of them run on the same engine; they differ in what is guided, what is added and what is switched on.

* **The Creation** (generic fantasy, the default). An Earth-like world with one sun and one moon, a broadly pre-modern level of technology, and the six default races: humans, dwarves, elves, orcs, trolls and ogres. The main world is remade Earth-like in an instant, its life is created to fit each niche of a finished world, and its peoples are set where each is at home. Goblins, fishmen and giants are proposed beside them; whether they belong in the default is still being decided.
* **The naturalistic route** (sci-fi). The physics and the dice decide. Life evolves to a mind and then to a civilisation, and what arises may look like nothing on Earth.
* **Custom variants.** Your own setting, written as data over the same engine: its own races and how they arrive, its own languages, its own game rules. The first variant is the author's own setting, *Eventide*. The trait tree that drives evolution is plain data too, so fantasy branches, such as a biosphere where some lineages feed on mana, are only more entries in a file.

## For game-masters: from world to game

Generation finishes before any game rules are applied. The world is then converted into game statistics by a **profile**: a set of data files that says how a body becomes attributes, how a zone becomes an environment, how a culture's technology becomes skills and equipment, and what a game calls its regions. Nothing in the world is changed to suit the game, and swapping the profile swaps the game. A generic profile is the default; Eventide's system is the first variant's.

## For world-builders: looking closer

Every layer can be explored on its own: a star-system page with maps, globes, plates through time and a timeline; a wiki of life where each group has its defining traits, how its rank grew, where it lives and what it contains; a language sheet with its sounds, a sample noun and verb in every form, pronouns and politeness, and the names of a world; a culture history with its peoples, states, technologies, frontiers and wars, brought down to zones and towns. A whole world can also be written out as a linked wiki.

## Where it stands

Demiurge is in active development, and each module below exists and is tested (the test suite stands at 442 passing). The [reference](reference/) says, section by section, what is built, what is partial and what is still to build.

| Module | State |
|---|---|
| Star system, geology, atmosphere, surface, seasons | working |
| Rivers, lakes and marsh; landmarks, seasonal flow, currents and weather | working |
| Geography, realms and settlements | working |
| Life and the history of life, to the first minds | working; the last stretch to intelligence is still being calibrated |
| Culture: peoples, technology, states, religion, magic, myth, law, trade, wars | working |
| Language: sounds, grammar, names, writing and descent | working; syntax is not built |
| RPG adaptation | first version |
| Whole worlds from a seed, with locks and a wiki export | working |
| A finished interface | not yet: Demiurge runs from the command line, with a simple local page for the language module |

## Languages

Demiurge is written in British English. The release is planned to be available in English, French, German, Russian, Spanish, Portuguese, Italian, Persian, Hindi, Armenian, Georgian, Mandarin, Japanese and Korean; none of the interface or the generated descriptions has been localised yet.

## Where next

Read the [reference](reference/) for what each layer takes in and gives out, or see the [download](download/) page for the state of the first test version.
