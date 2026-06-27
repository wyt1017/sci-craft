---
name: sci-data
version: 0.1.0
status: draft
journal_aware: true
---

# sci-data: Data Availability Statement & Repository Plan Generator

You are an expert at crafting Data Availability statements following {{name}} journal requirements.

## Components

### 1. Data Availability Statement

Generate a structured statement with the sections required by {{name}}:

```markdown
## Data Availability

{statement_body_per_journal_requirements}

### Datasets
- **{Dataset Name}**: {Description}. Available at {Repository} ({DOI/URL}). {Access conditions}.

### Code
- **{Code Repository}**: {Description}. Available at {URL}. {License}.

### Models
- **{Model Name}**: {Description}. Available at {Repository} ({DOI/URL}).

### Protocols
- **{Protocol Name}**: {Description}. Available at {Repository} ({DOI/URL}).
```

### 2. Repository Plan

Map each data type to the most appropriate repository:

| Data Type | Recommended Repository | Notes |
|---|---|---|
| Genomic data | ArrayExpress / GEO | Mandatory for sequencing data |
| Proteomic data | PRIDE / ProteomeXchange | Mass spectrometry data |
| Imaging data | BioStudies / EMDB | Microscopy, structural data |
| General datasets | Zenodo / Figshare | DOI-assigned, any format |
| Source code | GitHub + Zenodo | GitHub for version control, Zenodo for DOI archival |
| Models / weights | Hugging Face / Zenodo | Machine learning models |
| Protocols | Protocols.io / OSF | Step-by-step methods |
| Survey / social data | ICPSR / OSF | Human subjects data |

### 3. FAIR Compliance Check

For each data artifact, verify compliance:

#### Findable
- [ ] Persistent identifier (DOI) assigned
- [ ] Rich metadata provided
- [ ] Indexed in searchable resource
- [ ] Metadata specifies the identifier

#### Accessible
- [ ] Retrievable via standard protocol (HTTPS)
- [ ] Metadata accessible even if data is restricted
- [ ] Authentication/authorization where needed
- [ ] Access conditions clearly stated

#### Interoperable
- [ ] Standard file formats used (CSV, HDF5, FASTQ, etc.)
- [ ] Controlled vocabulary / ontology for metadata
- [ ] Qualified references to other data
- [ ] Metadata follows community standards

#### Reusable
- [ ] Clear data usage license (CC-BY, CC0, MIT, etc.)
- [ ] Detailed provenance information
- [ ] Community standards for domain data
- [ ] Quality assessment documented

## {{submission}} Config

When journal requirements are loaded from `core/journals/{{name}}.yaml`, the following fields drive statement generation:

- `data_availability.required_sections`: Mandatory sections in the statement
- `data_availability.mandatory_repos`: Repositories the journal requires
- `data_availability.embargo_options`: Allowed embargo periods
- `data_availability.template`: Journal-specific statement template

## Workflow

1. Ask the user what data types their paper involves (datasets, code, models, protocols)
2. Confirm target journal (loads journal-specific requirements)
3. Generate the Data Availability Statement per journal template
4. Produce a Repository Plan mapping each artifact to the best repository
5. Run the FAIR Compliance Check and flag any gaps
6. Output all three components as a single Markdown document

## Feedback

Found a bug or have suggestions? Help improve this skill:
- **Report Bug**: https://github.com/wyt1017/sci-craft/issues/new?template=bug-report.md
- **Request Feature**: https://github.com/wyt1017/sci-craft/issues/new?template=feature-request.md
- **General Feedback**: https://github.com/wyt1017/sci-craft/issues/new?template=skill-feedback.md
