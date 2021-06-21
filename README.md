# Lex Rosetta: Transfer of Predictive Models Across Languages, Jurisdictions, and Legal Domains

This is an accompanying repository to the [ICAIL 2021](https://icail.lawgorithm.com.br/) paper entitled "Lex Rosetta: Transfer of Predictive Models Across Languages, Jurisdictions, and Legal Domains". All the data and the code used in the experiments reported in the paper are to be found here.

## Data
The data set consists of 807 adjudicatory decisions from 7 different countries (6 languages) annotated in terms of the following [type system](https://github.com/lexrosetta/caselaw_functional_segmentation_multilingual/blob/master/annotation_guidelines/LexRosetta-AnnotationGuidelines-1.0.pdf):

* **Out of Scope** - Parts outside of the main document body (e.g., metadata, editorial content, dissents, end notes, appendices).
* **Heading** - Typically an incomplete sentence or marker starting a section (e.g., “Discussion,” “Analysis,” “II.”).
* **Background** - The part where the court describes procedural history, relevant facts, or the parties’ claims.
* **Analysis** - The section containing reasoning of the court, issues, and application of law to the facts of the case.
* **Introductory Summary** - A brief summary of the case at the beginning of the decision.
* **Outcome** - A few sentences stating how the case was decided (i.e, the overall outcome of the case).

The country specific subsets:

* **Canada** - Random selection of cases retrieved from [www.canlii.org](www.canlii.org) from multiple provinces. The selection is not limited to any specific topic or court.
* **Czech Republic** - A random selection of cases from Constitutional Court (30), Supreme Court (40), and Supreme Administrative Court (30). Temporal distribution was taken into account.
* **France** - A selection of cases decided by Cour de cassation between 2011 and 2019. A stratified sampling based on the year of publication of the decision was used to select the cases.
* **Germany** - A stratified sample from the federal jurisprudence database spanning all federal courts (civil, criminal, labor, finance, patent, social, constitutional, and administrative).
* **Italy** - The top 100 cases of the criminal courts stored between 2015 and 2020 mentioning “stalking” and keyed to the Article 612 bis of the Criminal Code.
* **Poland** - A stratified sample from trial-level, appellate, administrative courts, the Supreme Court, and the Constitutional tribunal. The cases mention “democratic country ruled by law.”
* **U.S.A. I** - Federal district court decisions in employment law mentioning “motion for summary judgment,” “employee,” and “independent contractor.”
* **U.S.A. II** - Administrative decisions from the U.S. Department of Labor. Top 100 ordered in reverse chronological rulings order, starting in October 2020, were selected.

For more detailed information, please, refer to the original paper.

## How to Use

### ICAIL 2021 Data
The data used in the ICAIL 2021 experiments can be found in the following paths:

    data/Country-Language-*/annotator-*-ICAIL2021.csv

Note that the Canadian subset could not be included in this repository due to concerns about personal information protection in Canada. However, it can be obtained upon request at [feedback-form@canlii.org](mailto://feedback-form@canlii.org). Once you obtain the data, you just need to create `data/Canada-EN-1` directory and place all the files there.

If you would like to experiment with different preprocessing techniques the original texts are placed in the following paths:

    data/Country-Language-*/texts

You can find the annotations corresponding to these texts here:

    data/Country-Language-*/annotator-*.csv

The texts cleaned of the `Out of Scope` and `Heading` segments (via `dataset_clean.py`) are placed in the following paths:

    data/Country-Language-*/texts-clean-annotator-*

Note that the processing depends on annotations. Hence, there are several versions of documents at this stage if there were multiple annotators. The annotations corresponding to the cleaned texts are here:

    data/Country-Language-*/annotator-*-clean.csv

The `dataset_ICAIL2021.py` has the processing code that has been applied to the cleaned texts and annotations to generate the ICAIL 2021 dataset (see above). Note, that the code will skip the Czech Republic subset by default. This is because this subset requires an external resource for sentence segmentation (`czech-pdt-ud-X.X-XXXXXX.udpipe`). You first need to obtain the file at [https://universaldependencies.org/](https://universaldependencies.org/). Then, you need to place it into the `data` directory. Then, you can remove the `Czech_Republic-CZ-1` string from the `EXCLUDED` tuple in `dataset_ICAIL2021.py`. Finally, you need to replace the `data/czech-pdt-ud-2.5-191206.udpipe` string in the `utils.py` to correspond to the file that you have downloaded. After these changes, the code will also operate on the Czech Republic part of the dataset.

### Dataset Statistics

To replicate the inter-annotator agreement analysis performed in the ICAIL 2021 paper you can use the `ia_agreement.ipynb` notebook.

To generate the dataset statistics reported in the ICAIL 2021 paper you can use the `dataset_statistics.ipynb` notebook.

### Experiments

<...>

## Attribution
We kindly ask you to cite the following paper:

Jaromir Savelka, Hannes Westermann, Karim Benyekhlef, Charlotte S. Alexander, Jayla C. Grant, David Restrepo Amariles, Rajaa El Hamdani, Sébastien Meeùs, Aurore Troussel, Michał Araszkiewicz, Kevin D. Ashley, Alexandra Ashley, Karl Branting, Mattia Falduti, Matthias Grabmair, Jakub Harašta,Tereza Novotná, Elizabeth Tippett, and Shiwanni Johnson. 2021. Lex Rosetta: Transfer of Predictive Models Across Languages, Jurisdictions, and Legal Domains. In *Eighteenth International Conference for Artificial Intelligence and Law (ICAIL’21), June 21–25, 2021, São Paulo, Brazil.* ACM, New York,NY, USA, 10 pages. [https://doi.org/10.1145/3462757.34661491](https://doi.org/10.1145/3462757.34661491)
