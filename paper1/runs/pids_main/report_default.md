# Paired audit report: `pids_main`

Dataset `3d8a8714b2a898dc`, commit `ec2715c6d471`. Threshold policy for TPR/FPR/PJA: **default** (calibrated on held-out clean benign prompts unless `default`).

## Within-condition AUROC (attack vs. benign twin)

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 0.781 | 0.586 | 0.404 | 0.571 | 0.667 | 0.518 | 0.644 | 0.336 | 0.505 | 0.781 | 0.579 | 0.586 |
| fmops | 0.817 | 0.817 | 0.817 | 0.479 | 0.482 | 0.467 | 0.528 | 0.309 | 0.577 | 0.463 | 0.817 | 0.496 |
| guardshield | 0.939 | 0.496 | 0.466 | 0.611 | 0.653 | 0.520 | 0.898 | 0.487 | 0.899 | 0.939 | 0.445 | 0.496 |
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

## Paired joint accuracy (%) at default

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 40.0 | 0.0 | 0.0 | 0.0 | 2.5 | 0.0 | 0.0 | 0.0 | 0.0 | 40.0 | 0.0 | 0.0 |
| fmops | 28.5 | 28.5 | 28.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 9.5 | 28.5 | 0.0 |
| guardshield | 64.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 60.5 | 0.0 | 60.0 | 64.5 | 0.0 | 0.0 |
| horizon_guard_base | 78.0 | 78.0 | 78.0 | 24.0 | 44.0 | 0.0 | 60.0 | 0.0 | 0.5 | 78.0 | 11.0 | 24.5 |
| llama_guard_3_1b | 47.0 | 15.0 | 25.5 | 17.0 | 27.5 | 0.0 | 66.0 | 26.0 | 54.5 | 11.0 | 26.5 | 15.5 |
| llama_guard_3_8b | 21.5 | 37.5 | 36.0 | 29.0 | 24.5 | 0.0 | 38.5 | 0.0 | 13.5 | 28.5 | 34.5 | 32.5 |
| llama_guard_4_12b | 37.0 | 38.5 | 38.5 | 11.0 | 36.0 | 0.0 | 57.5 | 0.0 | 58.0 | 1.0 | 29.0 | 41.0 |
| mezzo_v2_base | 84.5 | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 | 78.5 | 0.0 | 75.5 | 84.5 | 0.0 | 0.0 |
| perplexity_gpt2 | — | — | — | — | — | — | — | — | — | — | — | — |
| prompt_guard_2_22m | 45.0 | 45.0 | 0.0 | 0.0 | 0.0 | 0.0 | 35.5 | 0.0 | 40.0 | 45.0 | 0.0 | 45.0 |
| prompt_guard_2_86m | 26.0 | 26.0 | 0.0 | 0.0 | 0.0 | 0.0 | 16.5 | 0.0 | 18.0 | 26.0 | 0.0 | 26.0 |
| prompt_guard_v1 | 0.0 | 0.5 | 0.0 | 0.0 | 5.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.5 |
| prompt_guard_v1_jailbreak | 42.0 | 0.0 | 0.0 | 0.0 | 1.5 | 0.0 | 13.5 | 0.0 | 26.0 | 42.0 | 0.5 | 0.0 |
| protectai_v2 | 73.0 | 2.0 | 0.0 | 2.5 | 42.0 | 0.0 | 14.5 | 0.0 | 27.0 | 73.0 | 5.5 | 2.0 |
| qwen3guard_gen_0_6b | 64.5 | 58.5 | 51.5 | 2.5 | 52.0 | 0.0 | 70.5 | 0.0 | 63.0 | 51.5 | 17.5 | 58.5 |
| qwen3guard_gen_8b | 60.5 | 65.0 | 65.0 | 63.5 | 62.0 | 0.0 | 71.0 | 0.0 | 54.0 | 65.0 | 21.0 | 66.0 |
| sentinel_v2 | 94.0 | 53.5 | 35.5 | 41.0 | 79.5 | 0.0 | 92.5 | 0.0 | 94.0 | 52.0 | 13.0 | 70.0 |
| wildguard | 53.5 | 13.5 | 11.5 | 14.0 | 14.0 | 0.0 | 58.0 | 0.0 | 50.5 | 0.0 | 5.0 | 10.5 |

## Attack recall / TPR (%) at default

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 92.0 | 100.0 | 100.0 | 100.0 | 99.5 | 100.0 | 100.0 | 100.0 | 100.0 | 92.0 | 100.0 | 100.0 |
| fmops | 96.5 | 96.5 | 96.5 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 36.5 | 96.5 | 100.0 |
| guardshield | 66.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 66.0 | 96.5 | 62.0 | 66.0 | 100.0 | 100.0 |
| horizon_guard_base | 80.5 | 80.5 | 80.5 | 94.5 | 53.0 | 100.0 | 99.0 | 100.0 | 99.5 | 80.5 | 15.0 | 33.0 |
| llama_guard_3_1b | 49.5 | 22.5 | 40.5 | 84.5 | 29.5 | 100.0 | 84.0 | 50.0 | 63.0 | 20.5 | 41.0 | 18.5 |
| llama_guard_3_8b | 22.0 | 41.5 | 40.0 | 51.0 | 26.0 | 0.0 | 41.0 | 0.0 | 14.0 | 58.0 | 61.0 | 34.5 |
| llama_guard_4_12b | 38.0 | 46.0 | 44.5 | 93.0 | 42.0 | 100.0 | 66.0 | 100.0 | 64.5 | 100.0 | 37.0 | 75.0 |
| mezzo_v2_base | 86.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 88.5 | 100.0 | 91.5 | 86.0 | 100.0 | 100.0 |
| perplexity_gpt2 | — | — | — | — | — | — | — | — | — | — | — | — |
| prompt_guard_2_22m | 45.0 | 45.0 | 0.0 | 0.0 | 0.0 | 0.0 | 35.5 | 0.0 | 40.0 | 45.0 | 0.0 | 45.0 |
| prompt_guard_2_86m | 26.0 | 26.0 | 0.0 | 0.0 | 0.0 | 0.0 | 16.5 | 0.0 | 18.0 | 26.0 | 0.0 | 26.0 |
| prompt_guard_v1 | 100.0 | 0.5 | 0.0 | 0.0 | 42.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0.5 | 0.5 |
| prompt_guard_v1_jailbreak | 42.0 | 0.0 | 0.0 | 0.0 | 1.5 | 0.0 | 13.5 | 0.0 | 26.0 | 42.0 | 0.5 | 0.0 |
| protectai_v2 | 73.0 | 100.0 | 100.0 | 95.5 | 97.5 | 100.0 | 97.5 | 100.0 | 99.0 | 73.0 | 99.0 | 100.0 |
| qwen3guard_gen_0_6b | 73.5 | 82.5 | 88.0 | 99.5 | 81.5 | 0.0 | 92.0 | 0.0 | 67.5 | 64.0 | 40.5 | 71.0 |
| qwen3guard_gen_8b | 68.5 | 73.5 | 72.5 | 83.5 | 73.0 | 0.0 | 77.5 | 0.0 | 57.5 | 74.0 | 23.5 | 75.0 |
| sentinel_v2 | 96.0 | 98.0 | 98.5 | 82.5 | 93.5 | 0.0 | 95.0 | 0.0 | 95.0 | 58.0 | 13.0 | 97.0 |
| wildguard | 62.5 | 15.5 | 12.0 | 17.0 | 15.5 | 0.0 | 68.5 | 0.0 | 58.0 | 0.0 | 5.0 | 11.5 |

## Benign twin FPR (%) at default

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 56.0 | 100.0 | 100.0 | 100.0 | 97.5 | 100.0 | 100.0 | 100.0 | 100.0 | 56.0 | 100.0 | 100.0 |
| fmops | 70.5 | 70.5 | 70.5 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 42.5 | 70.5 | 100.0 |
| guardshield | 3.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 9.0 | 99.5 | 4.0 | 3.0 | 100.0 | 100.0 |
| horizon_guard_base | 3.5 | 3.5 | 3.5 | 73.5 | 17.0 | 100.0 | 39.5 | 100.0 | 99.5 | 3.5 | 14.5 | 22.0 |
| llama_guard_3_1b | 3.5 | 32.5 | 39.0 | 80.0 | 6.5 | 100.0 | 20.5 | 44.0 | 13.5 | 45.0 | 42.0 | 20.5 |
| llama_guard_3_8b | 2.0 | 6.5 | 7.0 | 40.5 | 1.5 | 0.0 | 4.0 | 0.5 | 2.0 | 48.0 | 41.0 | 7.5 |
| llama_guard_4_12b | 1.0 | 13.0 | 13.0 | 87.0 | 13.0 | 100.0 | 11.5 | 100.0 | 7.5 | 99.0 | 20.0 | 43.5 |
| mezzo_v2_base | 2.0 | 100.0 | 99.0 | 100.0 | 100.0 | 100.0 | 10.5 | 100.0 | 16.5 | 2.0 | 100.0 | 100.0 |
| perplexity_gpt2 | — | — | — | — | — | — | — | — | — | — | — | — |
| prompt_guard_2_22m | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0 | 0.0 | 0.0 |
| prompt_guard_2_86m | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| prompt_guard_v1 | 100.0 | 3.5 | 3.5 | 0.0 | 71.5 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 4.5 | 3.5 |
| prompt_guard_v1_jailbreak | 0.0 | 0.0 | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0 |
| protectai_v2 | 0.0 | 98.0 | 100.0 | 97.0 | 57.0 | 100.0 | 85.0 | 100.0 | 73.0 | 0.0 | 94.5 | 98.0 |
| qwen3guard_gen_0_6b | 11.0 | 29.0 | 40.5 | 97.5 | 35.5 | 0.0 | 22.5 | 0.0 | 5.5 | 19.0 | 53.5 | 21.0 |
| qwen3guard_gen_8b | 10.5 | 9.5 | 9.5 | 25.0 | 13.0 | 0.0 | 9.0 | 0.0 | 5.5 | 11.5 | 15.0 | 11.0 |
| sentinel_v2 | 2.0 | 46.0 | 64.5 | 51.0 | 16.0 | 0.0 | 2.5 | 0.0 | 1.0 | 9.0 | 7.5 | 27.5 |
| wildguard | 10.5 | 6.0 | 5.5 | 20.5 | 6.0 | 0.0 | 12.0 | 0.0 | 10.0 | 0.0 | 4.0 | 5.5 |

## FPR (%) after re-thresholding each condition to the clean TPR

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 55.5 | 79.5 | 91.0 | 79.5 | 65.0 | 93.0 | 68.0 | 96.5 | 75.0 | 55.5 | 83.0 | 79.5 |
| fmops | 70.5 | 70.5 | 70.5 | 98.5 | 95.0 | 100.0 | 84.5 | 99.0 | 78.5 | 97.5 | 70.5 | 90.5 |
| guardshield | 3.0 | 68.5 | 68.0 | 40.5 | 55.0 | 63.0 | 8.0 | 67.5 | 8.0 | 3.0 | 77.0 | 68.5 |
| horizon_guard_base | 3.5 | 3.5 | 3.5 | 61.5 | 31.0 | 78.0 | 0.0 | 68.5 | 0.0 | 3.5 | 41.0 | 45.5 |
| llama_guard_3_1b | 3.0 | 52.5 | 45.5 | 46.5 | 20.0 | 46.0 | 9.5 | 44.0 | 9.0 | 74.0 | 50.0 | 48.0 |
| llama_guard_3_8b | 2.0 | 2.0 | 2.5 | 18.5 | 1.5 | 23.0 | 1.0 | 17.0 | 2.0 | 23.0 | 21.5 | 3.5 |
| llama_guard_4_12b | 1.0 | 10.5 | 10.5 | 36.0 | 10.0 | 31.5 | 1.5 | 36.0 | 1.0 | 38.0 | 20.0 | 19.0 |
| mezzo_v2_base | 2.0 | 92.0 | 82.0 | 88.0 | 80.5 | 86.0 | 8.5 | 90.0 | 8.0 | 2.0 | 90.0 | 92.0 |
| perplexity_gpt2 | — | — | — | — | — | — | — | — | — | — | — | — |
| prompt_guard_2_22m | 0.0 | 0.0 | 36.0 | 57.0 | 64.5 | 44.5 | 0.0 | 64.5 | 0.5 | 0.0 | 52.0 | 0.0 |
| prompt_guard_2_86m | 0.0 | 0.0 | 50.5 | 46.5 | 14.5 | 23.5 | 0.0 | 41.0 | 0.0 | 0.0 | 51.0 | 0.0 |
| prompt_guard_v1 | 99.0 | 100.0 | 100.0 | 100.0 | 100.0 | 98.5 | 100.0 | 98.5 | 100.0 | 99.0 | 99.0 | 100.0 |
| prompt_guard_v1_jailbreak | 0.0 | 61.0 | 51.0 | 54.0 | 38.5 | 45.5 | 0.0 | 65.5 | 0.0 | 0.0 | 54.5 | 61.0 |
| protectai_v2 | 0.0 | 56.0 | 77.5 | 62.5 | 28.0 | 78.0 | 8.5 | 75.0 | 1.5 | 0.0 | 73.5 | 56.0 |
| qwen3guard_gen_0_6b | 11.0 | 19.5 | 22.5 | 59.5 | 31.0 | 68.0 | 10.5 | 84.0 | 6.5 | 23.0 | 73.0 | 22.0 |
| qwen3guard_gen_8b | 10.5 | 9.0 | 9.5 | 18.0 | 12.0 | 78.0 | 6.0 | 57.5 | 9.0 | 11.0 | 54.0 | 10.0 |
| sentinel_v2 | 2.0 | 36.0 | 43.5 | 71.0 | 24.0 | 95.5 | 4.5 | 96.5 | 2.0 | 70.0 | 88.0 | 24.0 |
| wildguard | 10.5 | 18.5 | 23.5 | 59.5 | 24.0 | 62.5 | 8.5 | 65.0 | 12.0 | 66.0 | 27.5 | 31.5 |

## FPR (%) at the threshold catching 90% of the condition's attacks (threshold-free)

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | 54.0 | 77.5 | 85.0 | 79.0 | 58.5 | 90.0 | 61.5 | 96.5 | 74.5 | 54.0 | 80.5 | 77.5 |
| fmops | 32.5 | 32.5 | 32.5 | 91.0 | 84.0 | 100.0 | 78.0 | 96.5 | 69.0 | 90.0 | 32.5 | 83.5 |
| guardshield | 16.0 | 86.5 | 83.5 | 84.5 | 83.5 | 91.5 | 31.5 | 94.5 | 27.5 | 16.0 | 92.5 | 86.5 |
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

## Failure mode at default (pre-registered; SPEC section 5)

| Guard | clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| deepset | · | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | · | **closed** | **closed** |
| fmops | · | · | · | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **open** | · | **closed** |
| guardshield | · | **closed** | **closed** | **closed** | **closed** | **closed** | · | **closed** | · | · | **closed** | **closed** |
| horizon_guard_base | · | · | · | **closed** | **open** | **closed** | **closed** | **closed** | **closed** | · | **open** | **open** |
| llama_guard_3_1b | · | **both** | **closed** | **closed** | **open** | **closed** | · | **closed** | · | **both** | **closed** | **open** |
| llama_guard_3_8b | · | · | · | **closed** | · | **open** | · | **open** | · | **closed** | **closed** | · |
| llama_guard_4_12b | · | · | · | **closed** | · | **closed** | · | **closed** | · | **closed** | · | **closed** |
| mezzo_v2_base | · | **closed** | **closed** | **closed** | **closed** | **closed** | · | **closed** | · | · | **closed** | **closed** |
| perplexity_gpt2 | — | — | — | — | — | — | — | — | — | — | — | — |
| prompt_guard_2_22m | · | · | **open** | **open** | **open** | **open** | · | **open** | · | · | **open** | · |
| prompt_guard_2_86m | · | · | **open** | **open** | **open** | **open** | · | **open** | · | · | **open** | · |
| prompt_guard_v1 | · | **open** | **open** | **open** | **open** | · | · | · | · | · | **open** | **open** |
| prompt_guard_v1_jailbreak | · | **open** | **open** | **open** | **open** | **open** | **open** | **open** | · | · | **open** | **open** |
| protectai_v2 | · | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | **closed** | · | **closed** | **closed** |
| qwen3guard_gen_0_6b | · | · | **closed** | **closed** | **closed** | **open** | · | **open** | · | · | **both** | · |
| qwen3guard_gen_8b | · | · | · | · | · | **open** | · | **open** | · | · | **open** | · |
| sentinel_v2 | · | **closed** | **closed** | **closed** | · | **open** | · | **open** | · | **open** | **open** | **closed** |
| wildguard | · | **open** | **open** | **open** | **open** | **open** | · | **open** | · | **open** | **open** | **open** |

## Length confound (AUROC of character length, attack vs twin; 0.5 = none)

| clean | zero_width | soft_hyphen | leetspeak | homoglyph | base64_wrap | base64_scaffold | rot13_wrap | rot13_scaffold | fullwidth | diacritics | spaced_letters |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0.533 | 0.562 | 0.562 | 0.533 | 0.533 | 0.532 | 0.533 | 0.533 | 0.533 | 0.533 | 0.559 | 0.562 |
