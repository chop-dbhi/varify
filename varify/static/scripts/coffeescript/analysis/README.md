# Guided Analysis View

The dialog consists of multiple _logical_ sections that each expose one or
more form elements that correspond to query filters. As the values in the
form controls are altered, the Serrano DataContext nodes are updated and
persisted on the server (to not lose the current state of the query), but
only after the dialog is closed is the query rerun (to prevent uncessary
queries on the server).

The forms controls are pre-populated with data prior to page load, but the
default filters or a user's selected filters must be applied at runtime.
Since this dialog is re-used across multiple analyses during a given session
the dialog must either be stateless (load on open, flush on close) or be
aware of the curent _active_ analysis. The latter is more desirable (and
how it is implemented) to prevent the overhead of reloading the query data
each.

To ensure the best experience, the code _is_ aware of the filters that
are exposed, rather than generically traversing the various types. Below
lists the descriptions of each filter and it's behavior.

## Proband Section

Selection of the proband and pedigree samples (if available). This step
must be completed to continue.

- "Select the proband"
- Dropdown of all available probands by batch and project
- This is the sample of interest and will be viewable in the "Review"
- "Include samples from pedigree"
- Checkbox (unchecked)
- Only if there are pedigree samples for the proband will this be
available

## Batch Section

Enables selecting a batch to compare against the proband. Common usages
include selecting controls to remove common variants or using known or
predicted affected to show the overlap of variants.

- "Select a batch to compare against"
- If no batches exist, there will be a message that states that
and suggests creating a new batch for comparison
- "Create a new batch..."
- Consists of a multi-select list based on a batch/project
- This is most likely iterative since users won't usually know
which samples belong in a batch ahead of time
- See also `batch-manager.coffee`

## Depth & Quality

Defines the depth of coverage and quality of the reads.

- "Depth of Coverage"
- Dropdown list of defaults for research and clinical use with an
"Other" option
- Selecting the "Other" option exposes a text box that defines the
minimum coverage
- "Quality"
- Same as DoC

## Common Variants

Uses resources (e.g. 1000G and EVS) to remove common variants.

- "1000G"
- Dropdown of defaults such as &lt;=5% and &lt;=1% with an "Other" option
- Selecting the "Other" option exposes a text box that defines the
threshold
- "EVS"
- Same as 1000G

## Deleterious Predictions

Uses resources (e.g. SIFT and PolyPhen2) to remove variants which
are predicted to have no negative impact.

- "SIFT"
- Dropdown of defaults specific to SIFT scores
- "PolyPhen2"
- Dropdown of defaults specific to PolyPhen2 scores

## Variant Effect Predictions

Uses resources (e.g. SNPEff) to select regions that are predicted to be
affected by the variant. All controls are multi-select fields.

- "Functional Class"
- "Effect Impact"
- "Effect Region"

## Genes

Adds the ability to constrain the variants to specific genes. There are
two interfaces including a free text search that queries the gene index and
a dropdown of fixed gene lists. The ability to create gene lists from here
may be necessary.

- "Gene Lists"
- Dropdown of gene lists
- "Genes"
- Auto-complete search box
