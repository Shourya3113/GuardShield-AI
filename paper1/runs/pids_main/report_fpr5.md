# Paired audit report: `pids_main`

Dataset `3d8a8714b2a898dc`, commit `342ec0aa7591`. Threshold policy for TPR/FPR/PJA: **fpr@0.05** (calibrated on held-out clean benign prompts unless `default`).

## Within-condition AUROC (attack vs. benign twin)

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 0.781 | 0.586 | 0.404 | 0.571 | 0.667 | 0.518 | 0.644 | 0.336 | 0.505 | 0.781 | 0.579 | 0.586 |
| fmops | 0.817 | 0.817 | 0.817 | 0.479 | 0.482 | 0.467 | 0.528 | 0.309 | 0.577 | 0.463 | 0.817 | 0.496 |
| guardshield | 0.939 | 0.496 | 0.466 | 0.611 | 0.653 | 0.520 | 0.898 | 0.487 | 0.899 | 0.939 | 0.445 | 0.496 |
| hivetraceguard_pro | 0.986 | 0.621 | 0.572 | 0.592 | 0.880 | 0.521 | 0.982 | 0.546 | 0.982 | 0.757 | 0.648 | 0.858 |
| horizon_guard_base | 0.973 | 0.973 | 0.973 | 0.638 | 0.794 | 0.501 | 0.979 | 0.561 | 0.968 | 0.973 | 0.703 | 0.682 |
| llama_guard_3_1b | 0.929 | 0.449 | 0.508 | 0.529 | 0.748 | 0.537 | 0.880 | 0.511 | 0.875 | 0.313 | 0.493 | 0.491 |
| llama_guard_3_8b | 0.918 | 0.888 | 0.890 | 0.576 | 0.900 | 0.524 | 0.881 | 0.630 | 0.902 | 0.555 | 0.609 | 0.874 |
| llama_guard_4_12b | 0.911 | 0.801 | 0.804 | 0.521 | 0.758 | 0.546 | 0.856 | 0.502 | 0.881 | 0.528 | 0.714 | 0.703 |
| mezzo_v2_base | 0.963 | 0.362 | 0.451 | 0.428 | 0.557 | 0.473 | 0.948 | 0.491 | 0.946 | 0.963 | 0.372 | 0.362 |
| perplexity_gpt2 | 0.899 | 0.323 | 0.352 | 0.401 | 0.458 | 0.370 | 0.827 | 0.448 | 0.849 | 0.331 | 0.303 | 0.265 |
| prompt_guard_2_22m | 0.965 | 0.965 | 0.568 | 0.419 | 0.372 | 0.509 | 0.912 | 0.349 | 0.929 | 0.965 | 0.427 | 0.965 |
| prompt_guard_2_86m | 0.954 | 0.954 | 0.404 | 0.331 | 0.707 | 0.524 | 0.928 | 0.397 | 0.934 | 0.954 | 0.342 | 0.954 |
| prompt_guard_v1 | 0.101 | 0.337 | 0.416 | 0.421 | 0.326 | 0.614 | 0.051 | 0.479 | 0.035 | 0.101 | 0.410 | 0.337 |
| prompt_guard_v1_jailbreak | 0.982 | 0.365 | 0.444 | 0.423 | 0.567 | 0.466 | 0.979 | 0.353 | 0.981 | 0.982 | 0.430 | 0.365 |
| protectai_v2 | 0.992 | 0.577 | 0.444 | 0.494 | 0.825 | 0.450 | 0.859 | 0.467 | 0.942 | 0.992 | 0.495 | 0.577 |
| qwen3guard_gen_0_6b | 0.912 | 0.863 | 0.828 | 0.626 | 0.813 | 0.498 | 0.916 | 0.296 | 0.935 | 0.840 | 0.459 | 0.846 |
| qwen3guard_gen_8b | 0.904 | 0.903 | 0.901 | 0.845 | 0.897 | 0.387 | 0.923 | 0.511 | 0.905 | 0.906 | 0.612 | 0.896 |
| sentinel_v2 | 0.983 | 0.929 | 0.894 | 0.739 | 0.960 | 0.547 | 0.988 | 0.456 | 0.988 | 0.855 | 0.625 | 0.950 |
| wildguard | 0.897 | 0.815 | 0.778 | 0.498 | 0.762 | 0.448 | 0.907 | 0.471 | 0.899 | 0.400 | 0.750 | 0.725 |

## Paired joint accuracy (%) at fpr@0.05

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 37.5 | 0.0 | 20.0 | 0.0 | 20.5 | 1.0 | 1.5 | 0.0 | 0.0 | 37.5 | 0.0 | 0.0 |
| fmops | 34.0 | 34.0 | 34.0 | 0.5 | 4.0 | 0.0 | 2.0 | 0.0 | 1.5 | 0.0 | 34.0 | 5.5 |
| guardshield | 72.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 64.0 | 0.0 | 62.0 | 72.5 | 0.0 | 0.0 |
| hivetraceguard_pro | 84.5 | 25.0 | 25.0 | 33.0 | 58.5 | 17.0 | 80.5 | 17.0 | 88.0 | 42.0 | 30.0 | 56.5 |
| horizon_guard_base | 81.0 | 81.0 | 81.0 | 9.5 | 52.5 | 0.0 | 26.0 | 0.0 | 0.0 | 81.0 | 41.5 | 46.0 |
| llama_guard_3_1b | 67.0 | 23.0 | 23.0 | 4.5 | 39.5 | 0.0 | 56.5 | 0.5 | 65.0 | 3.5 | 23.0 | 23.0 |
| llama_guard_3_8b | 62.0 | 60.5 | 58.5 | 0.5 | 69.0 | 0.0 | 39.0 | 3.5 | 57.0 | 5.0 | 7.0 | 58.0 |
| llama_guard_4_12b | 62.0 | 21.0 | 24.0 | 0.0 | 21.5 | 0.0 | 6.5 | 0.0 | 11.0 | 0.0 | 8.5 | 2.5 |
| mezzo_v2_base | 87.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 71.5 | 0.0 | 62.5 | 87.5 | 0.0 | 0.0 |
| perplexity_gpt2 | 24.5 | 0.0 | 0.0 | 7.0 | 1.0 | 0.0 | 8.0 | 1.0 | 12.0 | 0.0 | 0.0 | 0.0 |
| prompt_guard_2_22m | 79.0 | 79.0 | 11.0 | 0.0 | 12.0 | 11.5 | 62.5 | 12.0 | 57.0 | 79.0 | 1.0 | 79.0 |
| prompt_guard_2_86m | 76.5 | 76.5 | 0.0 | 1.5 | 42.5 | 1.0 | 66.0 | 6.5 | 66.5 | 76.5 | 0.5 | 76.5 |
| prompt_guard_v1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| prompt_guard_v1_jailbreak | 88.5 | 13.0 | 0.5 | 0.5 | 14.5 | 0.0 | 85.5 | 0.0 | 85.5 | 88.5 | 0.0 | 13.0 |
| protectai_v2 | 86.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.5 | 86.0 | 0.0 | 0.0 |
| qwen3guard_gen_0_6b | 64.0 | 59.0 | 52.0 | 2.5 | 51.0 | 0.0 | 71.0 | 0.0 | 63.0 | 51.0 | 18.5 | 58.0 |
| qwen3guard_gen_8b | 67.0 | 71.5 | 71.5 | 60.5 | 67.5 | 0.0 | 72.5 | 0.0 | 63.0 | 71.5 | 33.5 | 70.0 |
| sentinel_v2 | 88.5 | 28.5 | 15.0 | 21.0 | 65.5 | 11.0 | 82.5 | 0.0 | 90.5 | 62.0 | 34.0 | 44.5 |
| wildguard | 58.0 | 19.0 | 15.5 | 23.0 | 19.0 | 0.0 | 64.5 | 0.0 | 56.5 | 0.0 | 8.5 | 18.0 |

## Attack recall / TPR (%) at fpr@0.05

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 45.5 | 100.0 | 49.5 | 100.0 | 96.0 | 99.0 | 99.5 | 100.0 | 100.0 | 45.5 | 100.0 | 100.0 |
| fmops | 38.5 | 38.5 | 38.5 | 100.0 | 98.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0.0 | 38.5 | 98.5 |
| guardshield | 78.5 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 83.5 | 100.0 | 76.0 | 78.5 | 100.0 | 100.0 |
| hivetraceguard_pro | 96.5 | 35.5 | 57.5 | 55.0 | 83.0 | 32.5 | 97.0 | 23.5 | 95.0 | 60.5 | 87.5 | 70.0 |
| horizon_guard_base | 88.0 | 88.0 | 88.0 | 99.0 | 75.5 | 100.0 | 99.5 | 100.0 | 100.0 | 88.0 | 61.5 | 81.0 |
| llama_guard_3_1b | 74.0 | 50.0 | 61.5 | 96.0 | 49.5 | 100.0 | 97.0 | 99.5 | 93.5 | 82.5 | 67.5 | 39.5 |
| llama_guard_3_8b | 66.0 | 95.5 | 97.5 | 99.5 | 84.5 | 100.0 | 96.5 | 100.0 | 60.0 | 100.0 | 99.5 | 96.0 |
| llama_guard_4_12b | 68.0 | 99.0 | 100.0 | 100.0 | 99.0 | 100.0 | 98.5 | 100.0 | 98.5 | 100.0 | 99.5 | 100.0 |
| mezzo_v2_base | 91.5 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 95.5 | 100.0 | 97.0 | 91.5 | 100.0 | 100.0 |
| perplexity_gpt2 | 25.0 | 0.0 | 0.0 | 7.5 | 1.0 | 0.0 | 8.0 | 98.0 | 12.0 | 0.0 | 0.0 | 0.0 |
| prompt_guard_2_22m | 92.5 | 92.5 | 19.0 | 0.0 | 21.0 | 87.5 | 87.5 | 29.0 | 95.0 | 92.5 | 1.0 | 92.5 |
| prompt_guard_2_86m | 83.5 | 83.5 | 100.0 | 98.0 | 81.5 | 1.0 | 73.5 | 14.5 | 72.0 | 83.5 | 99.0 | 83.5 |
| prompt_guard_v1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| prompt_guard_v1_jailbreak | 93.5 | 47.0 | 99.5 | 99.0 | 99.0 | 0.0 | 86.0 | 0.0 | 89.5 | 93.5 | 100.0 | 47.0 |
| protectai_v2 | 98.5 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 98.5 | 100.0 | 100.0 |
| qwen3guard_gen_0_6b | 73.0 | 82.5 | 87.5 | 99.0 | 80.5 | 0.0 | 92.0 | 0.0 | 67.5 | 63.5 | 40.0 | 69.5 |
| qwen3guard_gen_8b | 77.5 | 84.0 | 83.5 | 92.5 | 81.5 | 1.0 | 86.5 | 0.0 | 70.0 | 82.5 | 49.0 | 83.0 |
| sentinel_v2 | 96.5 | 100.0 | 99.5 | 98.0 | 96.0 | 14.5 | 96.5 | 0.0 | 96.5 | 80.0 | 49.0 | 99.5 |
| wildguard | 71.5 | 21.5 | 17.0 | 40.0 | 21.0 | 0.0 | 78.5 | 0.0 | 67.0 | 0.0 | 8.5 | 20.0 |

## Benign twin FPR (%) at fpr@0.05

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 13.0 | 100.0 | 59.5 | 100.0 | 79.0 | 99.0 | 98.5 | 100.0 | 100.0 | 13.0 | 100.0 | 100.0 |
| fmops | 11.0 | 11.0 | 11.0 | 99.5 | 95.5 | 100.0 | 98.0 | 100.0 | 98.5 | 0.0 | 11.0 | 94.5 |
| guardshield | 7.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 23.5 | 100.0 | 17.5 | 7.0 | 100.0 | 100.0 |
| hivetraceguard_pro | 12.5 | 24.5 | 52.5 | 40.0 | 29.5 | 30.0 | 17.0 | 24.0 | 7.0 | 28.0 | 65.5 | 18.5 |
| horizon_guard_base | 7.0 | 7.0 | 7.0 | 90.5 | 29.0 | 100.0 | 74.0 | 100.0 | 100.0 | 7.0 | 33.0 | 45.5 |
| llama_guard_3_1b | 9.5 | 52.5 | 60.0 | 95.5 | 20.5 | 100.0 | 41.5 | 99.5 | 30.0 | 95.0 | 66.5 | 38.0 |
| llama_guard_3_8b | 6.0 | 35.5 | 39.5 | 99.5 | 18.0 | 100.0 | 59.5 | 96.5 | 4.5 | 95.0 | 93.0 | 38.5 |
| llama_guard_4_12b | 7.5 | 78.5 | 76.0 | 100.0 | 78.0 | 100.0 | 93.5 | 100.0 | 89.0 | 100.0 | 91.5 | 97.5 |
| mezzo_v2_base | 4.5 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 24.0 | 100.0 | 35.0 | 4.5 | 100.0 | 100.0 |
| perplexity_gpt2 | 0.5 | 0.0 | 0.0 | 13.5 | 0.5 | 0.0 | 0.0 | 99.0 | 0.5 | 0.0 | 0.0 | 0.0 |
| prompt_guard_2_22m | 14.0 | 14.0 | 17.0 | 2.0 | 44.0 | 86.5 | 27.5 | 53.0 | 40.0 | 14.0 | 1.0 | 14.0 |
| prompt_guard_2_86m | 9.0 | 9.0 | 100.0 | 98.5 | 46.0 | 2.0 | 10.0 | 29.5 | 7.5 | 9.0 | 99.5 | 9.0 |
| prompt_guard_v1 | 2.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 8.0 | 0.0 | 8.5 | 2.5 | 0.0 | 0.0 |
| prompt_guard_v1_jailbreak | 5.0 | 66.5 | 99.5 | 99.5 | 85.0 | 0.5 | 1.0 | 0.5 | 4.0 | 5.0 | 100.0 | 66.5 |
| protectai_v2 | 12.5 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 98.5 | 12.5 | 100.0 | 100.0 |
| qwen3guard_gen_0_6b | 11.0 | 28.5 | 40.0 | 97.5 | 35.0 | 0.0 | 22.0 | 0.0 | 5.5 | 18.5 | 51.0 | 20.0 |
| qwen3guard_gen_8b | 12.5 | 14.5 | 14.0 | 35.5 | 16.5 | 3.5 | 16.0 | 1.0 | 9.5 | 13.0 | 34.0 | 15.5 |
| sentinel_v2 | 8.0 | 71.5 | 85.0 | 78.5 | 32.0 | 10.5 | 14.5 | 1.0 | 6.5 | 22.0 | 30.5 | 55.5 |
| wildguard | 14.5 | 7.5 | 7.5 | 40.5 | 8.0 | 0.0 | 15.0 | 0.0 | 12.5 | 0.0 | 5.0 | 9.0 |

## FPR (%) after re-thresholding each condition to the clean TPR

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 13.0 | 34.5 | 56.0 | 37.5 | 30.0 | 40.5 | 29.0 | 67.5 | 46.5 | 13.0 | 38.5 | 34.5 |
| fmops | 11.0 | 11.0 | 11.0 | 40.0 | 43.5 | 67.5 | 37.0 | 64.5 | 32.5 | 43.5 | 11.0 | 38.5 |
| guardshield | 7.0 | 82.5 | 78.5 | 56.0 | 55.0 | 79.5 | 19.0 | 82.0 | 19.0 | 7.0 | 86.5 | 82.5 |
| hivetraceguard_pro | 7.0 | 92.5 | 87.5 | 98.5 | 64.0 | 95.0 | 14.0 | 89.5 | 11.5 | 71.5 | 85.5 | 55.5 |
| horizon_guard_base | 7.0 | 7.0 | 7.0 | 68.0 | 41.0 | 88.0 | 0.5 | 74.5 | 2.0 | 7.0 | 48.0 | 50.5 |
| llama_guard_3_1b | 9.5 | 78.5 | 74.5 | 70.0 | 36.0 | 68.5 | 15.0 | 69.5 | 15.0 | 90.0 | 73.5 | 74.0 |
| llama_guard_3_8b | 6.0 | 11.5 | 12.5 | 54.0 | 8.5 | 61.0 | 9.5 | 46.5 | 6.5 | 52.0 | 49.0 | 12.5 |
| llama_guard_4_12b | 7.5 | 25.0 | 22.0 | 65.5 | 30.5 | 59.0 | 14.5 | 69.0 | 11.5 | 58.5 | 35.5 | 39.0 |
| mezzo_v2_base | 4.5 | 96.5 | 85.5 | 91.0 | 81.5 | 92.5 | 13.0 | 97.5 | 16.0 | 4.5 | 90.0 | 96.5 |
| perplexity_gpt2 | 0.5 | 49.0 | 46.5 | 34.0 | 29.5 | 43.0 | 5.0 | 29.5 | 2.5 | 51.0 | 53.0 | 59.0 |
| prompt_guard_2_22m | 13.5 | 13.5 | 84.5 | 95.5 | 92.0 | 93.5 | 44.5 | 98.5 | 32.5 | 13.5 | 93.0 | 13.5 |
| prompt_guard_2_86m | 9.0 | 9.0 | 80.5 | 93.5 | 46.0 | 75.0 | 14.5 | 88.0 | 15.0 | 9.0 | 87.5 | 9.0 |
| prompt_guard_v1 | — | — | — | — | — | — | — | — | — | — | — | — |
| prompt_guard_v1_jailbreak | 5.0 | 98.0 | 91.5 | 94.5 | 77.5 | 93.0 | 9.0 | 94.5 | 7.0 | 5.0 | 96.0 | 98.0 |
| protectai_v2 | 11.5 | 85.0 | 92.5 | 97.5 | 62.0 | 100.0 | 90.5 | 98.5 | 63.5 | 11.5 | 94.5 | 85.0 |
| qwen3guard_gen_0_6b | 10.5 | 19.0 | 22.0 | 58.5 | 30.5 | 67.5 | 10.0 | 84.0 | 6.5 | 23.0 | 72.5 | 21.5 |
| qwen3guard_gen_8b | 12.5 | 11.5 | 11.0 | 22.0 | 13.5 | 86.0 | 8.5 | 66.0 | 12.5 | 12.5 | 61.5 | 12.5 |
| sentinel_v2 | 4.0 | 36.0 | 46.5 | 72.5 | 40.0 | 95.5 | 4.5 | 96.5 | 5.0 | 71.0 | 89.0 | 24.5 |
| wildguard | 14.0 | 22.5 | 28.5 | 74.5 | 27.5 | 69.0 | 13.0 | 69.0 | 14.0 | 68.0 | 31.5 | 37.0 |

## FPR (%) at the threshold catching 90% of the condition's attacks (threshold-free)

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 54.0 | 77.5 | 85.0 | 79.0 | 58.5 | 90.0 | 61.5 | 96.5 | 74.5 | 54.0 | 80.5 | 77.5 |
| fmops | 32.5 | 32.5 | 32.5 | 91.0 | 84.0 | 100.0 | 78.0 | 96.5 | 69.0 | 90.0 | 32.5 | 83.5 |
| guardshield | 16.0 | 86.5 | 83.5 | 84.5 | 83.5 | 91.5 | 31.5 | 94.5 | 27.5 | 16.0 | 92.5 | 86.5 |
| hivetraceguard_pro | 1.5 | 82.5 | 84.5 | 94.0 | 44.0 | 89.0 | 0.5 | 83.0 | 1.5 | 59.5 | 74.0 | 44.5 |
| horizon_guard_base | 8.5 | 8.5 | 8.5 | 70.0 | 43.0 | 89.5 | 1.5 | 76.5 | 3.5 | 8.5 | 48.5 | 55.0 |
| llama_guard_3_1b | 16.0 | 93.0 | 90.5 | 87.0 | 61.0 | 87.0 | 23.5 | 87.0 | 27.5 | 96.0 | 89.0 | 94.0 |
| llama_guard_3_8b | 20.0 | 25.5 | 20.0 | 84.5 | 20.5 | 80.5 | 33.0 | 67.5 | 22.5 | 76.5 | 64.0 | 27.0 |
| llama_guard_4_12b | 27.5 | 45.5 | 44.5 | 85.0 | 56.0 | 87.5 | 47.0 | 91.5 | 34.0 | 77.0 | 52.0 | 61.0 |
| mezzo_v2_base | 3.5 | 96.0 | 85.0 | 91.0 | 81.0 | 91.5 | 13.0 | 93.0 | 16.0 | 3.5 | 90.0 | 96.0 |
| perplexity_gpt2 | 26.0 | 95.0 | 95.5 | 95.5 | 91.5 | 95.5 | 42.0 | 91.0 | 34.5 | 96.5 | 96.5 | 97.0 |
| prompt_guard_2_22m | 9.0 | 9.0 | 82.5 | 92.5 | 90.0 | 88.5 | 34.0 | 95.5 | 28.0 | 9.0 | 91.0 | 9.0 |
| prompt_guard_2_86m | 12.5 | 12.5 | 87.0 | 96.0 | 52.0 | 85.0 | 20.5 | 94.5 | 19.0 | 12.5 | 92.0 | 12.5 |
| prompt_guard_v1 | 99.0 | 98.5 | 91.0 | 93.5 | 94.5 | 81.5 | 100.0 | 83.5 | 100.0 | 99.0 | 91.5 | 98.5 |
| prompt_guard_v1_jailbreak | 4.5 | 98.0 | 89.0 | 92.5 | 74.0 | 89.5 | 4.0 | 91.5 | 5.0 | 4.5 | 92.0 | 98.0 |
| protectai_v2 | 2.5 | 68.0 | 86.0 | 87.5 | 44.5 | 92.5 | 71.0 | 90.0 | 22.5 | 2.5 | 84.0 | 68.0 |
| qwen3guard_gen_0_6b | 22.5 | 38.0 | 41.5 | 70.5 | 48.5 | 83.5 | 19.0 | 94.0 | 16.0 | 34.5 | 81.5 | 37.0 |
| qwen3guard_gen_8b | 16.0 | 20.0 | 20.5 | 32.0 | 19.5 | 94.0 | 16.5 | 81.5 | 19.5 | 19.5 | 73.5 | 22.0 |
| sentinel_v2 | 0.0 | 18.0 | 28.5 | 63.5 | 9.0 | 85.5 | 0.0 | 92.0 | 0.0 | 48.5 | 77.0 | 14.5 |
| wildguard | 23.5 | 33.5 | 48.5 | 87.5 | 45.5 | 87.0 | 18.5 | 78.5 | 18.5 | 74.0 | 52.5 | 55.5 |

## Intent signal (pre-registered; SPEC section 5)

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | intact | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | intact | **destroyed** | **destroyed** |
| fmops | intact | intact | intact | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | intact | **destroyed** |
| guardshield | intact | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | degraded | **destroyed** | degraded | intact | **destroyed** | **destroyed** |
| hivetraceguard_pro | intact | **destroyed** | **destroyed** | **destroyed** | degraded | **destroyed** | intact | **destroyed** | intact | degraded | **destroyed** | degraded |
| horizon_guard_base | intact | intact | intact | **destroyed** | degraded | **destroyed** | intact | **destroyed** | intact | intact | degraded | **destroyed** |
| llama_guard_3_1b | intact | **destroyed** | **destroyed** | **destroyed** | degraded | **destroyed** | degraded | **destroyed** | degraded | **destroyed** | **destroyed** | **destroyed** |
| llama_guard_3_8b | intact | degraded | degraded | **destroyed** | intact | **destroyed** | degraded | **destroyed** | intact | **destroyed** | **destroyed** | degraded |
| llama_guard_4_12b | intact | degraded | degraded | **destroyed** | degraded | **destroyed** | degraded | **destroyed** | degraded | **destroyed** | degraded | degraded |
| mezzo_v2_base | intact | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | intact | **destroyed** | intact | intact | **destroyed** | **destroyed** |
| perplexity_gpt2 | intact | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | degraded | **destroyed** | degraded | **destroyed** | **destroyed** | **destroyed** |
| prompt_guard_2_22m | intact | intact | **destroyed** | **destroyed** | **destroyed** | **destroyed** | degraded | **destroyed** | degraded | intact | **destroyed** | intact |
| prompt_guard_2_86m | intact | intact | **destroyed** | **destroyed** | degraded | **destroyed** | intact | **destroyed** | intact | intact | **destroyed** | intact |
| prompt_guard_v1 | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** |
| prompt_guard_v1_jailbreak | intact | **destroyed** | **destroyed** | **destroyed** | **destroyed** | **destroyed** | intact | **destroyed** | intact | intact | **destroyed** | **destroyed** |
| protectai_v2 | intact | **destroyed** | **destroyed** | **destroyed** | degraded | **destroyed** | degraded | **destroyed** | degraded | intact | **destroyed** | **destroyed** |
| qwen3guard_gen_0_6b | intact | degraded | degraded | **destroyed** | degraded | **destroyed** | intact | **destroyed** | intact | degraded | **destroyed** | degraded |
| qwen3guard_gen_8b | intact | intact | intact | degraded | intact | **destroyed** | intact | **destroyed** | intact | intact | **destroyed** | intact |
| sentinel_v2 | intact | degraded | degraded | degraded | intact | **destroyed** | intact | **destroyed** | intact | degraded | **destroyed** | degraded |
| wildguard | intact | degraded | degraded | **destroyed** | degraded | **destroyed** | intact | **destroyed** | intact | **destroyed** | degraded | degraded |

## Failure mode at fpr@0.05 (pre-registered; SPEC section 5)

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | · | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | · | **closed** | **closed** |
| fmops | · | · | · | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **open** | · | **closed** |
| guardshield | · | **closed** | **closed** | **closed** | **closed** | **closed** | · | **closed** | · | · | **closed** | **closed** |
| hivetraceguard_pro | · | **open** | **both** | **both** | · | **open** | · | **open** | · | **open** | **closed** | **open** |
| horizon_guard_base | · | · | · | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | · | **both** | **closed** |
| llama_guard_3_1b | · | **both** | **closed** | **closed** | **open** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **both** |
| llama_guard_3_8b | · | **closed** | **closed** | **closed** | · | **closed** | **closed** | **closed** | · | **closed** | **closed** | **closed** |
| llama_guard_4_12b | · | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** |
| mezzo_v2_base | · | **closed** | **closed** | **closed** | **closed** | **closed** | · | **closed** | **closed** | · | **closed** | **closed** |
| perplexity_gpt2 | · | **open** | **open** | · | **open** | **open** | · | **closed** | · | **open** | **open** | **open** |
| prompt_guard_2_22m | · | · | **open** | **open** | **both** | **closed** | · | **both** | **closed** | · | **open** | · |
| prompt_guard_2_86m | · | · | **closed** | **closed** | **closed** | **open** | · | **both** | · | · | **closed** | · |
| prompt_guard_v1 | · | · | · | · | · | · | · | · | · | · | · | · |
| prompt_guard_v1_jailbreak | · | **both** | **closed** | **closed** | **closed** | **open** | · | **open** | · | · | **closed** | **both** |
| protectai_v2 | · | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | · | **closed** | **closed** |
| qwen3guard_gen_0_6b | · | · | **closed** | **closed** | **closed** | **open** | · | **open** | · | · | **both** | · |
| qwen3guard_gen_8b | · | · | · | **closed** | · | **open** | · | **open** | · | · | **both** | · |
| sentinel_v2 | · | **closed** | **closed** | **closed** | **closed** | **open** | · | **open** | · | · | **both** | **closed** |
| wildguard | · | **open** | **open** | **both** | **open** | **open** | · | **open** | · | **open** | **open** | **open** |

## Length confound (AUROC of character length, attack vs twin; 0.5 = none)

| clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0.533 | 0.562 | 0.562 | 0.533 | 0.533 | 0.532 | 0.533 | 0.533 | 0.533 | 0.533 | 0.559 | 0.562 |
