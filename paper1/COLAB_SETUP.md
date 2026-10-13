# Running the Paper 1 audit on Google Colab

One-time setup takes about 15 minutes. After that, each run is **Runtime → Run all**.

## 1. Put the GuardShield weights on Google Drive (once)

The trained GuardShield model is not in git (it is about 570 MB).

1. Open https://drive.google.com and, in **My Drive**, create a folder named exactly `GuardShield_Paper1`.
2. Inside it, create a folder named exactly `deberta_v3_prescan_v3`.
3. Upload **only one file** into that folder: `D:\projects\GuardShield_AI\models\deberta_v3_prescan_v3\model.safetensors` (about 540 MB). The config and tokenizer files are already in git. Don't upload the `checkpoints` subfolder (1.6 GB of training leftovers).
4. Check the result: **My Drive › GuardShield_Paper1 › deberta_v3_prescan_v3 › model.safetensors**.

The notebook checks the file's SHA-256 against the hash recorded with the reported results, so a wrong or outdated upload is caught.

## 2. Create a read-only GitHub token (once)

The repository is private, so Colab needs permission to download it.

1. On GitHub, open **Settings › Developer settings › Personal access tokens › Fine-grained tokens** (https://github.com/settings/personal-access-tokens), then **Generate new token**.
2. **Token name:** `colab-readonly`. **Expiration:** 90 days.
3. **Repository access:** *Only select repositories* › `GuardShield-AI`.
4. **Permissions › Repository permissions › Contents:** *Read-only*. Leave everything else as it is.
5. Click **Generate token** and copy it (it starts with `github_pat_`). GitHub shows it only once.

## 3. Open the notebook in Colab

1. Go to https://colab.research.google.com.
2. **File › Upload notebook**, and choose `D:\projects\GuardShield_AI\notebooks\paper1_guard_audit_colab.ipynb`.

## 4. Add the two secrets (once per Google account)

In the notebook, click the **🔑 key icon** in the left sidebar (Secrets), then **Add new secret** twice:

| Name (exactly) | Value |
|---|---|
| `HF_TOKEN` | your Hugging Face Read token (`hf_…`) |
| `GITHUB_TOKEN` | the GitHub token from step 2 (`github_pat_…`) |

Turn **Notebook access** on for both. Never paste either token into a code cell.

## 5. Choose the GPU

**Runtime › Change runtime type**, select your largest GPU (the 47 GB option), then **Save**.

## 6. Run

1. **Runtime › Run all**.
2. When asked, allow access to Google Drive (pick the account that has the `GuardShield_Paper1` folder).
3. Watch section 9 (*Check the large judges*). Each of the four big judges prints three `PASS`/`FAIL` lines. A judge that fails is skipped automatically; copy its printed lines to Claude so its config can be fixed, then **Run all** again later.

**Expected time:** a rough guess of a few hours in total. The encoder classifiers take minutes each; the 8B/12B judges take most of the time.

**If Colab disconnects or times out:** reconnect and use **Run all** again. Finished guards are skipped and a half-finished guard resumes where it stopped.

## 7. Bring the results back

When section 12 finishes:

1. Download `My Drive › GuardShield_Paper1 › obf_main.zip`.
2. Unzip it into `D:\projects\GuardShield_AI\runs\` so that `D:\projects\GuardShield_AI\runs\obf_main\metrics.json` exists.
3. Tell Claude. The results are analysed from there.

## Troubleshooting

| Message | Fix |
|---|---|
| `No GPU` | Step 5: select a GPU runtime. |
| `GuardShield weights not found` | Step 1: check the folder name and location on Drive. |
| `weights … are not the ones the reported results used` | Re-upload `models/deberta_v3_prescan_v3` from the laptop. |
| `git failed: … 403` or `Repository not found` | The GitHub token is missing, expired, or not given *Contents: Read-only* on this repository (step 2). |
| `401` / `GatedRepoError` for a Meta or AI2 model | Your Hugging Face account has not been approved for that model yet, or `HF_TOKEN` is missing. |
| `Another scorer … is already running` | A second copy of the notebook is running on the same Drive folder. Stop one of them. |
| Out of GPU memory on `llama_guard_4_12b` | Use the 47 GB GPU. On a smaller GPU, set `"load_in_8bit": true` for it in `configs/guards.json`. |
