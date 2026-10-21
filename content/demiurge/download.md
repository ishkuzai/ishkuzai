---
title: Download
lead: The first test version is being prepared.
summary: How to get Demiurge, what it needs to run, and where the first test release stands.
---
## Where it stands

There is no packaged release yet. Demiurge currently runs from the command line, with a simple local page for trying the language module. The first test version, with a proper interface (presets, locks and a view of each layer), is in preparation. No date is set, and the licence will be stated with the release.

When it is ready it will be offered here, and announced on the [ishkuzai](https://ishkuzai.com/contact/) pages.

## What it needs

* **Node.js 24 or later.** Demiurge is written in TypeScript and run directly by Node: there is nothing to install beside it, and no other dependency.
* **Any ordinary computer.** Windows, macOS and Linux should do. Results that are pictures (maps, globes, timelines, the wiki of life, language charts) are self-contained web pages, so any browser will open them.
* **Patience for the longest runs.** The star system, the planet and its land take moments. The history of life to a mind is the dominant cost: five to fifteen minutes for each, and a whole science-fiction world may need several tries, so an hour or more.

## How it is run

Everything is driven by a seed, so the same seed and options always give the same world. The commands below show the shape of it.

```
node src/generate-cli.ts --seed 7 --mode generic-fantasy --model standard
node src/generate-cli.ts --seed 7 --mode sci-fi --plan          # show what a mode sets, without running it
node src/generate-cli.ts --seed 7 --wiki my-world                # write the world as a linked wiki
```

Fixing a setting, such as the star's mass or the amount of magic, is done by a **lock**, and the record of the world says which settings were locked and which were generated. The [reference](../reference/) describes the modes, the three models (simple, standard and advanced) and the locks in its sections on the two defaults and the framework.

## Staying informed

The release will be announced where the author's other projects are: see [ishkuzai](https://ishkuzai.com/contact/) for the accounts.
