## License

BY DOWNLOADING THE CODE OR USING THE SERVICE AND/OR SOFTWARE APPLICATION ACCOMPANYING THIS LICENSE, YOU ARE CONSENTING TO BE BOUND BY ALL OF THE TERMS OF THIS LICENSE AT THE BOTTOM OF THIS README

"Copyright 2024. The authors and University of Zurich. All Rights Reserved."

# Pythia 

<img src="assets/Landing/Logo/pythia_white_background.png" alt="Pythia logo" width="150"/>

[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19762869.svg)](https://doi.org/10.5281/zenodo.19762869)

Pythia is a web-based tool for designing CRISPR-Cas9 gRNAs and microhomology-based repair templates, using deep learning to predict precise editing outcomes. It covers three workflows — targeted transgene integration, single-nucleotide editing, and N/C-terminal gene tagging — and works with any species; pre-calculated genome-wide databases are provided for *Homo sapiens*, *Mus musculus*, and *Xenopus tropicalis*. Pythia is freely available at [pythia-editing.org](https://pythia-editing.org) or can be run locally via Docker for faster computation and full data privacy.

*Pythia is built on inDelphi, a deep-learning model for predicting CRISPR-Cas9 DNA repair outcomes. In ancient Greece, Pythia was the Oracle of Delphi — the priestess who could allegedly foresee what no one else could. This tool aspires to the same: to let you see the precise outcome of your genome edit before you ever make the cut.*

---

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [Usage Examples](#usage-examples)
- [Instructions for mounting databases from Zenodo](#instructions-for-mounting-databases-from-zenodo)
- [Repository Structure](#repository-structure)
- [License](#license)

---

## System Requirements

### Operating systems tested

- Windows 10 / Windows 11
- macOS (Apple Silicon — M1/M2/M3/M4)

### Operating systems expected to work

- macOS (Intel, via Docker)
- Linux (x86_64, via Docker)




### Non-standard hardware

None required. A standard desktop or laptop is sufficient.

---

## Installation Guide

### Option A — Docker (recommended)

> [!TIP]
> **Never heard of Docker? Here's all you need to know — it takes 30 seconds to read.**
>
> Pythia is available as a website at [pythia-editing.org](https://pythia-editing.org), but our server is shared and not exactly a powerhouse, so it can be slow. Docker lets you run an identical copy of Pythia as a tiny private website that lives entirely on your own computer (`localhost:8050` in your browser). Your data never leaves your machine, and since you're using your own hardware instead of a shared server, calculations run **5–10× faster**.
>
> So what *is* Docker? Think of it as a self-contained box that includes Pythia, all its code, and all its dependencies — pre-installed, pre-configured, ready to go. You download the box once, click Run, and it works. Nothing to install manually, nothing to configure.
>
> The whole thing is done through **Docker Desktop, a normal point-and-click application — no terminal, no code**. Master's students with no prior experience installed it in under 10 minutes. If they can do it, you can too.

Pythia is distributed as a Docker image (`linux/amd64`). The image is **~4 GB** — make sure you have at least **10 GB free disk space**. Install time is typically **10–20 minutes** depending on your internet speed.

---

#### 🪟 Windows (Intel/AMD)

**1. Install Docker Desktop**

- Download from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
- Run the installer and accept the defaults. WSL 2 will be installed automatically if not present.
- Reboot if prompted.
- Launch Docker Desktop from the Start menu and wait until the whale icon in the system tray says "Docker Desktop is running."

**2a. Option 1 (RECOMMENDED) — Via Docker Desktop GUI (no terminal needed)**

1. Open **Docker Desktop**.
2. In the search bar at the top, search for `thomasnaert/pythia_webtool`.
3. Click **Pull** to download the image (~4 GB, allow 10–20 minutes).
4. Once downloaded, go to the **Images** tab, find `pythia_webtool`, and click **Run**.
5. Expand **Optional settings** and set:
   - **Host port:** `8050`
6. Click **Run**. The container starts in seconds.
7. Open [http://localhost:8050](http://localhost:8050) in your browser.

To stop it, go to the **Containers** tab in Docker Desktop and click the stop button.

**2b. Option 2 — Via command line**

Open Command Prompt or PowerShell and run:

```cmd
docker pull thomasnaert/pythia_webtool:v1.0.0
docker run -p 8050:8050 thomasnaert/pythia_webtool:v1.0.0
```

Open [http://localhost:8050](http://localhost:8050) in your browser. To stop, press `Ctrl + C`.

---

#### 🍎 macOS (Apple Silicon — M1/M2/M3/M4)

Pythia's image is built for `linux/amd64`. On Apple Silicon Macs it runs transparently via **Rosetta 2 emulation** — no functional differences, slight startup overhead only.

**1. Install Rosetta 2**

Open Terminal (`Cmd + Space` → "Terminal" → Enter) and run:

```bash
softwareupdate --install-rosetta --agree-to-license
```

If Rosetta is already installed, it will tell you. Otherwise it installs in ~30 seconds.

**2. Install Docker Desktop**

- Download the **Apple Silicon** version from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
- Open the `.dmg` and drag Docker to Applications
- Launch Docker Desktop from Applications and wait until the whale icon in the menu bar stops animating

**3. Enable Rosetta emulation in Docker Desktop**

This step is essential for Pythia to run.

- Click the Docker whale icon → **Settings** (gear icon)
- Go to **General**
- Under **Virtual Machine Options**, select **Apple Virtualization framework**
- Tick **"Use Rosetta for x86_64/amd64 emulation on Apple Silicon"**
- Click **Apply & Restart**

**4. Pull the Pythia image**

```bash
docker pull --platform linux/amd64 thomasnaert/pythia_webtool:v1.0.0
```

**5. Run Pythia**

```bash
docker run --platform linux/amd64 -p 8050:8050 thomasnaert/pythia_webtool:v1.0.0
```

**6. Open Pythia in your browser**

Go to [http://localhost:8050](http://localhost:8050) — Pythia is now running.

To stop it, press `Ctrl + C` in Terminal.

---

#### Linux (x86_64)

Install Docker following your distribution's instructions ([https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)), then:

```bash
docker pull thomasnaert/pythia_webtool:v1.0.0
docker run -p 8050:8050 thomasnaert/pythia_webtool:v1.0.0
```

Open [http://localhost:8050](http://localhost:8050) in your browser.

---

#### Mounting the full precomputed databases

The image includes sample databases sufficient to demonstrate all tools out of the box. To use the full genome-wide Pre-calculated Tagging browser, download the species databases from Zenodo and mount them at runtime:

```bash
docker run -p 8050:8050 -v /path/to/databases:/app/db thomasnaert/pythia_webtool:v1.0.0
```

Replace `/path/to/databases` with the local path to the folder containing the unzipped `.db` files. On Windows use a path like `C:\Users\you\pythia_db` (Docker Desktop translates this automatically).

| # | Species | Record |
|---|---------|--------|
| 1 | *Homo sapiens* | Exonic precomputed Pythia predictions — [10.5281/zenodo.19484608](https://doi.org/10.5281/zenodo.19484608) |
| 2 | *Homo sapiens* | Intronic precomputed Pythia predictions — [10.5281/zenodo.19485095](https://doi.org/10.5281/zenodo.19485095) |
| 3 | *Mus musculus* | Precomputed Pythia predictions — [10.5281/zenodo.19485175](https://doi.org/10.5281/zenodo.19485175) |
| 4 | *Xenopus tropicalis* | Precomputed Pythia predictions — [10.5281/zenodo.19485132](https://doi.org/10.5281/zenodo.19485132) |

---

### Option B — Local Conda install

**Prerequisites:** [Anaconda](https://www.anaconda.com/download) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed.

> **Note:** Resolving and installing all pinned dependencies via conda takes a long time. Allow **30–60 minutes** on a standard desktop.

> **No databases are included.** You must download both the gRNA databases (`db/`) and transcript sequence databases (`transcript_sequences/`) from Zenodo and place them in the respective folders before the application will function.
>
> Download the full gRNA databases from Zenodo in /db and /transcript_sequences

| # | Species | Record |
|---|---------|--------|
| 1 | *Homo sapiens* | Exonic precomputed Pythia predictions — [10.5281/zenodo.19484608](https://doi.org/10.5281/zenodo.19484608) |
| 2 | *Homo sapiens* | Intronic precomputed Pythia predictions — [10.5281/zenodo.19485095](https://doi.org/10.5281/zenodo.19485095) |
| 3 | *Mus musculus* | Precomputed Pythia predictions — [10.5281/zenodo.19485175](https://doi.org/10.5281/zenodo.19485175) |
| 4 | *Xenopus tropicalis* | Precomputed Pythia predictions — [10.5281/zenodo.19485132](https://doi.org/10.5281/zenodo.19485132) |

Transcript sequence databases: [10.5281/zenodo.19594447](https://doi.org/10.5281/zenodo.19594447)

#### Software dependencies

| Package | Version |
|---------|---------|
| Python | 3.6 |
| Dash | 2.15.0 |
| Flask | 1.1.4 |
| Flask-Compress | 1.15 |
| dash-ag-grid | 32.3.2 |
| dash-bootstrap-components | 0.13.1 |
| pandas | 0.23.4 |
| numpy | 1.15.3 |
| plotly | 5.18.0 |
| scikit-learn | 0.20.0 |
| scipy | 1.1.0 |
| biopython | 1.76 |
| altair | 3.2.0 |
| pyfastx | 0.8.4 |

Full dependency list with exact pinned versions: [`requirements.txt`](requirements.txt) (pip/Docker) or [`requirements_pip.txt`](requirements_pip.txt) (conda).

```bash
# 1. Clone the repository
git clone https://github.com/XenoThomasNaert/Pythia_Webtool.git
cd Pythia_Webtool

# 2. Download db/ and transcript_sequences/ from Zenodo and place them here

# 3. Create and activate the conda environment
conda env create -f requirements_pip.txt
conda activate py36flask

# 4. Launch
python index.py
```

Open [http://localhost:8050](http://localhost:8050) in your browser.

---

## Usage Examples

### What works out of the box

|  | Docker | Conda / GitHub clone |
|--|--------|----------------------|
| **Editing tool** | Fully functional | Fully functional |
| **Integration tool** | Fully functional | Fully functional |
| **Custom Tagging** | Fully functional (transcript sequences bundled) | Requires downloading transcript databases from Zenodo |
| **Pre-calculated Tagging** | Partial — minimal sample gRNA DB only (limited genes) prepackaged. Full genome-wide precalculations need to be downloaded from Zenodo | Requires downloading transcript and pre-calculated output databases from Zenodo |

---

### Example 1 — Integration tool *(fully functional with Docker)*

The Integration tool designs gRNAs and microhomology repair templates for targeted transgene insertion at intergenic or intronic landing sites.

1. Navigate to the **Integration** tab.
2. Select an inDelphi model (e.g. `HEK293`).
3. Choose a workflow: **"Pre-validated gRNAs / I already have my gRNA"** or **"Find gRNA for me"**.
4. Paste a genomic sequence of your target landing site (at least 80 bp of context either side of the cut site).
5. Click **Calculate**.

**Expected output:** A ranked list of gRNAs with predicted repair frequencies, microhomology arm sequences, and a downloadable results table (Excel).

**Expected run time:** 10–60 seconds depending on sequence length.

---

### Example 2 — Editing tool *(fully functional with Docker)*

The Editing tool generates ssODN repair templates for precise single-nucleotide edits using microhomology-mediated end joining.

1. Navigate to the **Editing** tab.
2. Select an inDelphi model (e.g. `HEK293`).
3. Paste your original genomic sequence and your desired mutated sequence. Use the **eGFP example** buttons to load a pre-filled example immediately.
4. Click **Calculate**.

**Expected output:** Optimal ssODN repair templates and gRNA candidates ranked by predicted editing efficiency.

**Expected run time:** 10–60 seconds depending on sequence length.

---

### Example 3 — Custom Tagging *(fully functional with Docker)*

The Custom Tagging tool designs gRNAs and repair templates for N- or C-terminal tagging of any gene, using your own sequence input or auto-filled sequences from the bundled transcript database.

1. Navigate to the **Tagging** tab and select **Custom Tagging**.
2. Select an inDelphi model (e.g. `HEK293`).
3. Choose **3′ Tagging (C-terminal)** or **5′ Tagging (N-terminal)**.
4. **Auto-fill from database** *(Docker only — transcript sequences are bundled)*: select a species, gene, and transcript isoform. The target and context sequences fill automatically.  
   **Or paste manually:** enter the target site sequence and 50 bp of flanking genomic context on each side.
5. Enter your tag sequence (e.g. `EGFP`, `mCherry`, or a custom epitope).
6. Click **Calculate**.

**Expected output:** Ranked gRNA candidates with predicted repair frequencies, microhomology arm sequences, and a visualisation of the tagged locus.

**Expected run time:** 10–60 seconds depending on sequence length.

---

### Example 4 — Pre-calculated Tagging browser *(requires full databases)*

Download the full gRNA databases from Zenodo and mount them as described in [Instructions for mounting databases from Zenodo](#instructions-for-mounting-databases-from-zenodo):

| # | Species | Record |
|---|---------|--------|
| 1 | *Homo sapiens* | Exonic precomputed Pythia predictions — [10.5281/zenodo.19484608](https://doi.org/10.5281/zenodo.19484608) |
| 2 | *Homo sapiens* | Intronic precomputed Pythia predictions — [10.5281/zenodo.19485095](https://doi.org/10.5281/zenodo.19485095) |
| 3 | *Mus musculus* | Precomputed Pythia predictions — [10.5281/zenodo.19485175](https://doi.org/10.5281/zenodo.19485175) |
| 4 | *Xenopus tropicalis* | Precomputed Pythia predictions — [10.5281/zenodo.19485132](https://doi.org/10.5281/zenodo.19485132) |

Transcript sequence databases: [10.5281/zenodo.19594447](https://doi.org/10.5281/zenodo.19594447)

0. Mount as described in [Mounting the full gRNA databases](#instructions-for-mounting-databases-from-zenodo)
1. Navigate to the **Tagging** tab.
2. Select species: `Homo sapiens`, mode: `Exon 3bp`, cell type: `HEK293`.
3. Type a gene name (e.g. `KDM1A`) and select it from the dropdown.
4. Select a transcript isoform (e.g. `KDM1A-237`).
5. The gRNA table populates, ranked by Pythia integration score.
6. Click any row to open the zoom view showing gRNA position along the gene.

**Expected output:** A ranked table of gRNAs with CRISPRScan scores, Pythia scores, in-frame percentages, and efficiency labels (Very Good / Good / Low). A scatter plot showing all gRNAs mapped to gene position appears on row selection.

**Expected run time:** < 5 seconds per gene query.

---

## Instructions for mounting databases from Zenodo

### Docker (CLI)

After downloading the full `db/` folder from Zenodo, mount it at runtime:

```bash
# Windows (PowerShell)
docker run -p 8050:8050 `
  -v C:\path\to\your\db:/app/db `
  thomasnaert/pythia_webtool:v1.0.0
```

```bash
# Linux / macOS
docker run -p 8050:8050 \
  -v /path/to/your/db:/app/db \
  thomasnaert/pythia_webtool:v1.0.0
```

### Docker Desktop (GUI)

1. Go to the **Images** tab, find `pythia_webtool`, and click **Run**.
2. Expand **Optional settings**.
3. Set **Host port** to `8050`.
4. Under **Volumes**, add a bind mount:
   - **Host path:** your local `db/` folder (e.g. `C:\Users\you\pythia_db`)
   - **Container path:** `/app/db`
5. Click **Run**.

### Local installation (Conda)

All databases are hosted on Zenodo as they are too large for GitHub:

| File/folder | Docker | Conda / GitHub clone |
|-------------|--------|----------------------|
| `db/` — gRNA databases | Download and mount (see below) | Download and place in repo root |
| `transcript_sequences/` — transcript sequences | Already bundled in image | Download and place in repo root |

#### Conda / local install — placing the files

After downloading from Zenodo, place the folders directly inside the cloned repository before launching:

```
pythia/
├── db/                        ← replace with downloaded folder
├── transcript_sequences/      ← replace with downloaded folder
└── ...
```

Then launch as normal:

```bash
python index.py
```

---
---

### Performance configuration (local install only; especially relevant when hosting for multiple users over LAN)*

USE_CONNECTION_POOL enables persistent database connections, reducing query latency when multiple users access the tool concurrently; this should be set to True for any shared or production deployment. PERFORMANCE_PROFILE controls the in-memory cache size used to store frequently accessed precomputed predictions. The 'medium' profile (256 MB) is appropriate for most single-user or small-lab installations; 'high' (512 MB) is recommended when serving multiple concurrent users or when working with the full genome-wide databases, and 'low' (128 MB) can be used on memory-constrained systems at the cost of slower lookups for less frequently accessed loci.

Settings in [`app.py`](app.py):

```python
USE_CONNECTION_POOL = True       # Recommended for multi-user / production hosting
PERFORMANCE_PROFILE = 'medium'   # 'high' (512 MB cache), 'medium' (256 MB), 'low' (128 MB)
```

---

## Repository Structure

```
.
├── app.py                    # Dash app instance, connection config
├── index.py                  # Entry point — registers callbacks and starts server
├── callbacks/                # Dash callbacks (one module per feature)
│   ├── precalculated/        # Pre-calculated gRNA browser
│   ├── integration.py        # Integration tool
│   ├── tagging_custom.py     # Custom tagging
│   ├── tagging_intron.py     # Intron tagging
│   └── editing.py            # Sequence editing
├── layouts/                  # Page layouts
├── utils/                    # Shared database utilities and validation
├── assets/                   # Static files (CSS, JS)
├── db/                       # SQLite gRNA databases (sample data committed; full DBs from Zenodo)
├── transcript_sequences/     # Transcript sequence databases (sample data committed; full DBs from Zenodo)
├── connection_helper.py      # SQLite PRAGMA optimisation
├── connection_pool.py        # Connection pooling (production)
├── Dockerfile
├── requirements.txt          # Pip dependencies (used by Docker)
└── requirements_pip.txt      # Conda environment YAML (used for local install)
```

---

## Citation

If you use Pythia, please cite:

> Naert T, Yamamoto T, Han S, Röck R, Horn M, Bethge P, Vladimirov N, Voigt FF, Figueiro-Silva J, Bachmann-Gagescu R, Vleminckx K, Helmchen F, Lienkamp SS. **Precise, predictable genome integrations by deep-learning-assisted design of microhomology-based templates.** *Nature Biotechnology*, 2025. doi:[10.1038/s41587-025-02771-0](https://doi.org/10.1038/s41587-025-02771-0) PMID: 40796977

---

## Dependencies

Pythia builds on the following tools — please cite them if relevant to your work:

**inDelphi** — repair outcome prediction engine used throughout Pythia:

> Shen MW\*, Arbab M\*, Hsu JY, Worstell D, Culbertson SJ, Krabbe O, Cassa CA, Liu DR, Gifford DK, Sherwood RI. **Predictable and precise template-free editing of pathogenic variants.** *Nature*, 2018. doi:[10.1038/s41586-018-0686-x](https://doi.org/10.1038/s41586-018-0686-x) (\*equal contribution)

**CRISPRscan** — gRNA efficiency scoring:

> Moreno-Mateos MA\*, Vejnar CE\*, Beaudoin JD, Fernandez JP, Mis EK, Khokha MK, Giraldez AJ. **CRISPRscan: designing highly efficient sgRNAs for CRISPR-Cas9 targeting in vivo.** *Nature Methods*, 2015. doi:[10.1038/nmeth.3543](https://doi.org/10.1038/nmeth.3543) PMID: 26322839 (\*equal contribution)

**inDelphi editing outcome validation in *Xenopus* and zebrafish:**

> Naert T\*, Tulkens D\*, Edwards NA, Carron M, Shaidani NI, Wlizla M, Boel A, Demuynck S, Horb ME, Coucke P, Willaert A, Zorn AM, Vleminckx K. **Maximizing CRISPR-Cas9 phenotype penetrance applying predictive modeling of editing outcomes in *Xenopus* and zebrafish embryos.** *Scientific Reports*, 2020; 10:14662. doi:[10.1038/s41598-020-71412-0](https://doi.org/10.1038/s41598-020-71412-0) (\*equal contribution)

---

## Full License

BY DOWNLOADING THE CODE OR USING THE SERVICE AND/OR SOFTWARE APPLICATION ACCOMPANYING THIS LICENSE, YOU ARE CONSENTING TO BE BOUND BY ALL OF THE TERMS OF THIS LICENSE

"Copyright 2024. The authors and University of Zurich. All Rights Reserved."

The software is being provided as a service for research, educational, instructional and non-commercial purposes only. By submitting jobs to Pythia you agree to the terms and conditions herein.

You are an actively enrolled student, post-doctoral researcher, or faculty member at a degree-granting educational institution or government research institution; and You will only use the Pythia Software Application and/or Service for educational, instructional, and/or non-commercial research purposes;

You understand that all results produced using the Code may only be used for non-commercial research and/or academic purposes;

You understand that to obtain any right to use the Code for commercial purposes, or in the context of industrially sponsored research, You must enter into an appropriate, separate and direct license agreement with the Owners.

You will not redistribute unmodified versions of the Code;

You will redistribute modifications, if any, under the same terms as this license and only to non-profits and government institutions;

You must credit the authors of the Code: Thomas Naert, Soeren Lienkamp and cite "Naert, T., Yamamoto, T., Han, S. et al. Precise, predictable genome integrations by deep-learning-assisted design of microhomology-based templates. Nat Biotechnol (2025). https://doi.org/10.1038/s41587-025-02771-0"

You understand that neither the names of the Owners nor the names of the authors may be used to endorse or promote products derived from this software without specific prior written permission.

