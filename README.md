# A Brief Analysis of Ambiguous Homonyms

## What do we count as a homonym?

This analysis considers validly published binomial species names (excluding hybrids) in the World Checklist of Vascular Plants (WCVP) that resolve to
an accepted name (
i.e. Unplaced names
are ignored). We consider duplicated binomial names (homonyms) and specifically ambiguous homonyms (i.e. those that resolve to different accepted
species).

## Overview

Out of the 958,654 species records in the WCVP, 57,767 of these are species binomials that are ambiguous homonyms. The breakdown of the taxon statuses
of these 57,767 records is given below.

![ambiguous_homonyms_taxon_status_pie_chart.png](taxonomy_inputs%2Foutputs%2Fplots%2Fambiguous_homonyms_taxon_status_pie_chart.png)

Out of 924,458 *unique* binomial species names in the WCVP, 26,588 of these are ambiguous homonyms.

The most common homonym is *Artemisia rupestris*, and this is also
the binomial name that can refer to the most different accepted species, possibly referring to:

- *Artemisia alba subsp. alba*
- *Artemisia atrata* Lam.
- *Artemisia granatensis* Boiss.
- *Artemisia norvegica subsp. norvegica*
- *Artemisia pedemontana subsp. assoana* (Willk.) Rivas Mart.
- *Artemisia rupestris* L.
- *Artemisia splendens* Willd.
- *Artemisia umbelliformis subsp. umbelliformis*


## Where and When do Ambiguous Homonyms Come From?

The graph below shows published names over time and the proportions of which are homonyms (note that a name may have not been homonymous at
publication but falls into homonymy due to a later publication). It is clear to see that over time, fewer homonyms are being published! This is
somewhat unsurprising due to the connectivity given by the internet, as well as better nomenclature standards and name databases like IPNI.

![WCVP Species Publications and Homonym Occurrence_normalized.jpg](taxonomy_inputs%2Foutputs%2Fplots%2FWCVP%20Species%20Publications%20and%20Homonym%20Occurrence_normalized.jpg)

The chart below shows the global distributions of the accepted species that are resolved to by ambiguous binomial homonyms. This may partly reflect
the global distribution of plant species (e.g. dense population in South America ---
see [WCVP species plot](https://github.com/alrichardbollans/automatchnames/tree/main/wcvp_download/unit_tests/test_outputs/all_species_native_distribution.jpg)),
but parts of Europe are possibly over-represented.

![ambiguous_homonyms_dists.jpg](taxonomy_inputs%2Foutputs%2Fplots%2Fambiguous_homonyms_dists.jpg)

## Usage of Homonyms in Literature

The ambiguous homonyms discussed can be disambiguated by using the correct authority, e.g. *Artemisia rupestris* Scop. only refers to
*Artemisia alba subsp. alba*, and so the presence of homonyms on their own is not necessarily an issue. However, these binomial names are not
always disambiguated in this way and can result in ambiguity in scientific literature.

As seen above the *naming* of plant species is improving over time with regards to homonymy. However, we wonder how ambiguous homonyms are treated in
scientific literature and aim to quantify the number of ambiguous uses in scientific articles from CORE.

Results to follow...

## Licence

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/

[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png

[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg