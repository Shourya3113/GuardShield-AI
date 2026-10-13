# Running the Paper 1 audit (Kaggle recommended, Colab as an alternative)

Notebook: `notebooks/paper1_guard_audit.ipynb`. It runs on either platform without changes.

**Why Kaggle:** it gives free **2× T4 GPUs** (32 GB together, enough for every guard), **30 GPU-hours a week**, and committed runs that continue for **up to 12 hours with the browser closed**.

The guards are split into two sessions:
- **A:** all small guards, plus Llama Guard 3 8B (completed 2026-10-13)
- **B:** WildGuard (moved from A after a check bug, fixed 2026-10-13), Qwen3Guard 8B, Llama Guard 4 12B, and three newer classifiers (Mezzo Prompt Guard v2, Horizon-Labs guard, Sentinel v2). Before running B, accept the Sentinel v2 licence at https://huggingface.co/rogue-security/prompt-injection-jailbreak-sentinel-v2

Each session takes roughly 3–5 hours. This is a rough guess; T4 speed for these exact models has not been measured yet.

---

## Kaggle: one-time setup (about 15 minutes)

1. **Account and phone verification.** Sign up at https://www.kaggle.com (Google sign-in works). Then open https://www.kaggle.com/settings and complete **Phone verification**. Without it, Kaggle allows neither GPUs nor internet access.
2. **Upload the GuardShield weights as a private dataset.**
   1. Go to https://www.kaggle.com/datasets and click **+ New Dataset**.
   2. Drag in **only** `D:\projects\GuardShield_AI\models\deberta_v3_prescan_v3\model.safetensors` (about 540 MB). Do not upload the `checkpoints` folder.
   3. Title it `guardshield-weights`, keep it **Private**, and click **Create**.
3. **Create the read-only GitHub token** (the repository is private).
   1. Open https://github.com/settings/personal-access-tokens and click **Generate new token**.
   2. Name it `kaggle-readonly` and set it to expire in 90 days.
   3. Under **Repository access**, choose *Only select repositories* and pick `GuardShield-AI`.
   4. Under **Repository permissions**, set **Contents** to *Read-only*.
   5. Generate it and copy the token (it starts with `github_pat_`).
4. **Import the notebook.** At https://www.kaggle.com/code, click **+ New Notebook**, then **File › Import Notebook**, and upload `D:\projects\GuardShield_AI\notebooks\paper1_guard_audit.ipynb`.
5. **Notebook settings** (right-hand panel; open it with the arrow at the top right if hidden):
   - **Session options › Accelerator:** **GPU T4 x2**
   - **Session options › Internet:** **On**
   - **Input › + Add Input › Your Work › Datasets:** add `guardshield-weights`
6. **Secrets.** Open **Add-ons › Secrets** in the menu bar and add two secrets, then tick **Attach to notebook** for both:

   | Label (exactly) | Value |
   |---|---|
   | `HF_TOKEN` | your Hugging Face Read token (`hf_…`) |
   | `GITHUB_TOKEN` | the GitHub token from step 3 (`github_pat_…`) |

   Never paste either token into a code cell.

## Kaggle: each run

1. In the first code cell, set `GUARD_SET = "A"`.
2. Click **Save Version** (top right), choose **Save & Run All (Commit)**, and click **Save**. The run continues on Kaggle's servers, so you can close the browser.
3. About 20 minutes later, check that it started properly. Open the notebook from **Your Work**, then **Versions** › the running version › **Logs**. Section 8 should print three `PASS` lines per large judge. If a judge prints `FAIL`, it is skipped automatically; copy its lines to Claude.
4. When the version finishes, open it, go to the **Output** tab, and download `obf_main_A.zip`.
5. Go back to the editor, set `GUARD_SET = "B"`, and **Save Version** again. Do this after A has finished: Kaggle limits how many GPU sessions run at once. Then download `obf_main_B.zip`.

Your remaining GPU quota is shown at https://www.kaggle.com/settings under *Quotas*.

## Bring the results back

1. Unzip `obf_main_A.zip` into `D:\projects\GuardShield_AI\runs\`.
2. Unzip `obf_main_B.zip` into the same `runs\` folder. When asked about overwriting, choose **Yes to all**: the shared files (`dataset.jsonl`, `manifest.json`) are identical between sessions, and the per-guard score files differ.
3. Tell Claude. The combined metrics are recomputed from `runs\obf_main`; the harness refuses to combine score files from datasets that don't match.

---

## Colab alternative (free T4)

Free Colab works, but GPU availability is not guaranteed and sessions are short (often around 2 hours), so expect several restarts. Each restart resumes where the last one stopped.

1. On Google Drive, create `My Drive/GuardShield_Paper1/deberta_v3_prescan_v3/` and upload **only** `model.safetensors` into it.
2. Create the GitHub token as in Kaggle step 3.
3. At https://colab.research.google.com, use **File › Upload notebook** and choose `notebooks/paper1_guard_audit.ipynb`.
4. Click the **🔑 Secrets** icon, add `HF_TOKEN` and `GITHUB_TOKEN`, and switch on **Notebook access** for both.
5. **Runtime › Change runtime type › T4 GPU**. Not TPU: the harness needs an NVIDIA GPU.
6. Set `GUARD_SET` (start with `"A"`), then **Runtime › Run all**, and allow Drive access when asked.
7. Results are saved to `My Drive/GuardShield_Paper1/`. Download `obf_main_A.zip` / `obf_main_B.zip` from there.

With a single 16 GB T4, Llama Guard 4 12B does not fit in 16-bit. Run set B on Kaggle, or ask Claude to switch that judge to 8-bit loading.

---

## Troubleshooting

| Message | Fix |
|---|---|
| `No GPU` | Kaggle: Accelerator › GPU T4 x2. Colab: change the runtime to **T4 GPU** (a TPU such as *v5e* will not work). |
| `GuardShield weights not found` | Kaggle: add the `guardshield-weights` dataset as an input. Colab: check the Drive folder path. |
| `weights … are not the ones the reported results used` | Re-upload `models/deberta_v3_prescan_v3/model.safetensors` from the laptop. |
| `git failed: … 403` / `Repository not found` | The GitHub token is missing, expired, not attached, or lacks *Contents: Read-only* on this repository. |
| `401` / `GatedRepoError` | `HF_TOKEN` is missing or not attached, or your Hugging Face account was not approved for that model. |
| Download errors or `Temporary failure in name resolution` (Kaggle) | Internet is off, or the phone number is not verified. |
| `No space left on device` | Keep `DELETE_MODEL_AFTER = True` and run sets A and B in separate sessions. |
| `non-finite verdict log-likelihoods` | 16-bit overflow on this GPU; send the log to Claude. The fix is a per-guard setting in `configs/guards.json`. |
| `Another scorer … is already running` | Two sessions are writing the same results folder; stop one. |
