# A Brief Analysis of Ambiguous Homonyms

## What is counted as a homonym?

This analysis considers validly published binomial species names (excluding hybrids) in the World Checklist of Vascular Plants (WCVP) v13 [1] that
resolve to an accepted name (i.e. Unplaced names are ignored). I consider duplicated binomial names as homonyms, and specifically explore ambiguous
homonyms (i.e. those that resolve to different accepted species).

## Overview

Out of the 964,967 species records in the WCVP, 57,928 of these are species binomials that are ambiguous homonyms. The breakdown of the taxon statuses
of these 57,928 records is given below.

![ambiguous_homonyms_taxon_status_pie_chart.png](taxonomy_inputs%2Foutputs%2Fplots%2Fambiguous_homonyms_taxon_status_pie_chart.png)

Out of 930,686 *unique* binomial species names in the WCVP, 26,670 of these are ambiguous homonyms.

The most common homonym is *Artemisia rupestris*, and this is also
the binomial name that can refer to the most different accepted species, possibly referring to:

- *Artemisia alba subsp. alba*
- *Artemisia atrata* Lam.
- *Artemisia granatensis* Boiss.
- *Artemisia norvegica subsp. norvegica*
- *Artemisia assoana* Willk.
- *Artemisia rupestris* L.
- *Artemisia splendens* Willd.
- *Artemisia umbelliformis* Lam.

## Where and When do Ambiguous Homonyms Come From?

The graph below shows published names over time and the proportions of which are homonyms (note that a name may have not been homonymous at
publication but falls into homonymy due to a later publication). It is clear to see that over time, fewer homonyms are being published! This is
somewhat unsurprising due to the connectivity given by the internet, as well as better nomenclature standards and name databases like IPNI.

![WCVP Species Publications and Homonym Occurrence_normalized.jpg](taxonomy_inputs%2Foutputs%2Fplots%2FWCVP%20Species%20Publications%20and%20Homonym%20Occurrence_normalized.jpg)

The chart below shows the global distributions of the accepted species that are resolved to by ambiguous binomial homonyms. This may partly reflect
the global distribution of plant species (e.g. dense population in South America ---
see [WCVP species plot](https://github.com/alrichardbollans/wcvpy/blob/main/wcvpy/wcvp_download/unit_tests/test_outputs/all_species_native_distribution.jpg)),
but parts of Europe are possibly over-represented.

![ambiguous_homonyms_dists.jpg](taxonomy_inputs%2Foutputs%2Fplots%2Fambiguous_homonyms_dists.jpg)

## Usage of Homonyms in Literature

**_Note_**: The following suggests a process for analysing ambiguity of homonyms in open access literature, though searching through ~33 million
papers using regex or other string matching will require a computational/energy expense that I'm not yet convinced is worth it.

The ambiguous homonyms discussed can be disambiguated by using the correct authority, e.g. *Artemisia rupestris* Scop. only refers to
*Artemisia alba subsp. alba*, and so the presence of homonyms on their own is not necessarily an issue. However, these binomial names are not
always disambiguated in this way and can result in ambiguity in scientific literature.

As seen above, the *naming* of plant species is improving over time with regards to homonymy. However, I wonder how ambiguous homonyms are treated in
scientific literature and would like to quantify the number of ambiguous uses in scientific articles from CORE [2].

To do this, I search the 32.8 million full text papers hosted by CORE (v.2022) from 10,744 providers. For a given text, I begin by applying some
simple cleaning which aims to extract the body text from the full text (i.e. the text given before 'References', 'Supplementary material', 'Conflict
of interest' and 'Acknowledgments' headings) and then cleans the text by removing any punctuation (except hybrid characters "×" and "+"), setting all
letters to lower case and single-spacing all whitespace. With this body text, I then search for mentions of any ambiguous species binomials (as
defined above).

In papers containing these homonyms, I then search for any terms that potentially dismbiguate the homonym i.e.

- taxon names with authors
- taxon names with paranthet authors
- taxon names with primary author
- Each of the above with an abbreviated genus name.

I also check for the use of the homonym preceding infraspecific or hybrid characters which may indicate a disambiguation.

When searching for disambiguating terms, I clean the text as described above but without removing any sections. To align with the cleaned
text, the disambiguating terms are also cleaned by removing any punctuation (except hybrid characters "×" and "+"), setting all
letters to lower case and single-spacing all whitespace.

Results to follow...

## Discussion

This work highlights one specific aspect of ambiguity with regards to plant nomenclature. Though the underlying cause of this ambiguity is improving
over time, the ambiguity is persistent and requires disambiguation by people reading scientific papers, datasets, herbarium sheets, blog posts etc..
Increasingly this disambiguation, or _name resolution_, also needs to be carried out by automated systems that are attempting to extract structured
data from these types of sources. There are a plethora of software packages for this job (see [3]
and [here](https://github.com/alrichardbollans/wcvpy/blob/main/other_methods.md) for some examples), however when faced with ambiguous homonyms,
automated systems must make choices on which name to resolve to. A human resolver may overcome this ambiguity by searching the context surrounding a
given name, e.g. what does a paper reference? when was it published? does the paper mention a particular taxonomic authority or dataset version?
This kind of context is not available to standard resolution methods. In either case, the most reliable way to overcome this ambiguity is to
_include taxonomic authorities in plant names_.

While the use of taxonomic authorities is standard practice in published work related to taxonomy and nomenclature, this appears to be much less
common for other kinds of research and, as far as I understand, is actually discouraged by some journals. Personally, I would strongly encourage the
use of full scientific names (i.e. including taxonomic authority) anywhere that 'scientific' names are used so that the related documents contain
persistent, unambiguous references.

## References

[1] Rafaël Govaerts et al., ‘The World Checklist of Vascular Plants, a Continuously Updated Resource for Exploring Global Plant Diversity’, Scientific
Data 8, no. 1 (2021): 1–10, https://doi.org/10.1038/s41597-021-00997-6.

[2] Petr Knoth et al., ‘CORE: A Global Aggregation Service for Open Access Papers’, Scientific Data 10, no. 1 (7 June 2023):
366, https://doi.org/10.1038/s41597-023-02208-w.

[3] Matthias Grenié et al., ‘Harmonizing Taxon Names in Biodiversity Data: A Review of Tools, Databases and Best Practices’, Methods in Ecology and
Evolution, 18 February 2022, 2041-210X.13802, https://doi.org/10.1111/2041-210X.13802.

## Licence

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/

[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png

[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg